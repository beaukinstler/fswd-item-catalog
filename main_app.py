from flask import Flask, g, url_for, render_template, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from db_setup import BASE, User, Item, Category
from db_command import *
import random, string
import pdb
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

from flask.ext.httpauth import HTTPBasicAuth
from flask import make_response


CLIENT_ID = json.loads( open('client_secrets.json', 'r').read())['web']['client_id']


auth = HTTPBasicAuth()


app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

 
@app.route('/login',methods=['GET','POST'])
def showLogin():
    if request.method == 'GET':
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in range(32))
        login_session['state'] = state
        print("The current session state is {0}".format(login_session['state']))
        return render_template('login.html', STATE=state)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Try to get user from username first
        user = get_user(username)

        # Try to get user from email
        if user is None:
            user = get_user(email)
        if user is not None:
            if user.verify_password(password):
                login_session['username'] = user.username
                login_session['email'] = user.email
                flash("you are now logged in as %s" % login_session['username'])
                return redirect(url_for('index'))
            else:
                return "password didn't match"


@app.route('/gconnect', methods=['GET','POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    content = (h.request(url, 'GET')[1])
    result = json.loads(content.decode('utf-8'))
    
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token ent ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    # see if user exists, if not make it
    userID = get_user_id_from_email(login_session['email'])
    # import pdb
    # pdb.set_trace()
    if userID is None:
        # print('No user ID found, creating user')
        userID = createUser(login_session)
        login_session['user_id'] = userID
    else:
        login_session['user_id'] = userID
        

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print( "done!")


    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        # print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # print('In gdisconnect access token is %s', access_token)
    # print('User name is: ')
    # print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token={0}'.format(login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print('result is ')
    # print(result)
    if result['status'] == '200':
        # del login_session['access_token']
        # del login_session['gplus_id']
        # del login_session['username']
        # del login_session['email']
        # del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def Logout():
    login_session.clear()
    return render_template('loggedout.html'), 401

@auth.verify_password
def verify_password(usernameOrToken,password):
    # first see if the usernameOrToken is a token
    # if it is, it will pass back and ID, if not
    # it will send back None
    # pdb.set_trace()
    user_id = User.verify_auth_token(usernameOrToken)
    if user_id:
        print("Looking for user_id {0}".format(user_id))
        user = session.query(User).filter_by(id=user_id).first()
    else:
        #print("Looking for user {0} with password {1}".format(usernameOrToken,password))
        user = session.query(User).filter_by(username=usernameOrToken).first()
        #print("Found user: {0}".format(user.username)) 
        if not user or not user.verify_password(password):
            return False
        print("Authorized access to :{0}".format(user.username))

    g.user = user
    return True


#add /token route here to get a token for a user with login credentials
@app.route('/token', methods = ['GET'])
@auth.login_required
def get_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii')}), 201 #HTTP code CREATED

@app.route('/user/create/admin')
def createInitialAdmin():
    if get_user('admin') is None:
        """create the admin user with defaults"""
        add_user('admin','password','admin@example.com')
        admin = get_user('admin')
        # admin.active = 1
        #update_object(admin)
        if admin is None:
            print "couldn't create the admin"
        return render_template('initialize.html')
    else:
        print "admin was found"
        return "already made"         

@app.route('/user/create', methods = ['GET','POST'])
def create_user():

    if get_user('admin') is None:
        return redirect(url_for('createInitialAdmin'))
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('index'))        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if username is not None and \
        password is not None and \
        get_user(username) is None and \
        get_user_id_from_email(email) is None:
            new_id = add_user(username,password,email)
            id = get_user(username).id
            return redirect(url_for('getUser', user_id=id))
        else:
            print """Error: could not find password or username in 
                    post request, or username already exists"""
            return """Error: could not find password or username in 
                    post request, or username already exists"""

    if request.method == 'GET':
        return render_template('adduser.html')


    
@app.route('/user/<int:user_id>')
def getUser(user_id):
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('index'))   
    user = get_user_from_id(user_id)
    if user is not None:
        print user.username
        print login_session
        return jsonify(user.serialize)
    else:
        print 'no user with id {0}'.format(user_id)
        return 'none'

@app.route('/users')
# @auth.login_required
def getUsers():
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('index'))    
    users = get_all_users()

    return jsonify(User=[user.serialize for user in users])


# @app.route('/')
# def main():
#     categories = get_all_categories()
#     return render_template('categories.html',categories=categories)
@app.route('/landing')
def landing():
    categories = get_all_categories()
    # recent_items = get_recent_items()
    return render_template('landing.html',categories=categories)

@app.route('/')
@app.route('/categories')
def index():
    print request.headers
    categories = get_all_categories()

    return render_template('categories.html',categories=categories)

@app.route('/category/<int:cat_id>/')
@app.route('/category/<int:cat_id>/show')
def category(cat_id):

    category = get_category(cat_id)

    return render_template('category.html',category=category)       

@app.route('/category/<int:cat_id>/category_items')
def categoryItems(cat_id):
    category = session.query(Category).filter_by(id=cat_id).one()
    items = session.query(Item).filter_by(cat_id=category.id)
    # return output
    user = 'admin'
    return render_template('category_items.html',category=category,items=items,user=user)

@app.route('/category/<int:cat_id>/category_items/new', methods=['GET', 'POST'])
@auth.login_required
def newItem(cat_id):
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('index'))
    if request.method == 'POST':
        new_id = add_item(cat_id,request.form['name'],request.form['description'],request.form['price'])
        flash("New item created!")
        return redirect(url_for('categoryItems', cat_id=cat_id))
    else:
        return render_template('new_category_item.html',cat_id=cat_id)

@app.route('/category/<int:cat_id>/category_items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(cat_id, item_id):
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('index'))
    if request.method == 'POST':
        update_item(cat_id,item_id, request.form['name'], request.form['description'], request.form['price'])
        flash("Item updated!")
        return redirect(url_for('categoryItems', cat_id=cat_id))
    else:
        item = get_item(item_id)
        return render_template('edititem.html',item=item)

@app.route('/category/<int:cat_id>/category_items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(cat_id, item_id):
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('index'))    
    if request.method == 'POST':
        if request.form['delete'] == 'Delete':
            delete_item(item_id)
            flash("Item deleted!")
        elif request.form['delete'] == 'Cancel':
            pass
        return redirect(url_for('categoryItems', cat_id=cat_id))
    else:
        item = get_item(item_id)
        return render_template('deleteitem.html',item=item)


## JSON routes
@app.route('/category/<int:cat_id>/json', methods=['GET'])
def getAllItemJson(cat_id):
    cat = get_category(cat_id).serialize
    # cat_json = cat.serialize
    items = get_all_items(cat_id)
    return_json = cat.copy()
    return_json.update(Items=[item.serialize for item in items])
    return jsonify(return_json)
    # return  jsonify(Items=[item.serialize for item in items])


@app.route('/category/<int:cat_id>/category_items/<int:item_id>/json', methods=['GET'])
def getItemJson(cat_id, item_id):
    item = get_item(item_id)
    return jsonify(Items=item.serialize)

## JSON routes
@app.route('/categories/json', methods=['GET'])
def getAllCategorysJson(cat_id):
    categories = get_all_categories()
    return jsonify(Restuarants=[res.serialize for res in categories])

@app.route('/categories', methods=['GET'])
def getAllCategories():
    categories = get_all_categories()

    return render_template('categories.html',categories=categories)



@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('index'))
    if request.method == 'POST':
        new_id = add_category(request.form['name'])
        flash("Category added!")
        return redirect(url_for('getAllCategories'))
    else:
        return render_template('newcategory.html')

@app.route('/category/<int:cat_id>/edit', methods=['GET', 'POST'])
def editCategory(cat_id):
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('category',cat_id=cat_id))
    if request.method == 'POST':
        update_category(cat_id, request.form['name'])
        flash("Category updated!")
        return redirect(url_for('getAllCategories'))
    else:
        category = get_category(cat_id)
        return render_template('editcategory.html',category=category)

@app.route('/category/<int:cat_id>/delete', methods=['GET','POST'])
def deleteCategory(cat_id):
    if 'username' not in login_session:
        flash("Please login first!")
        return redirect(url_for('category',cat_id=cat_id))
    if request.method == 'POST':
        if request.form['delete'] == 'Delete':
            delete_category(cat_id)
            flash("Category deleted!")
        elif request.form['delete'] == 'Cancel':
            pass
        return redirect(url_for('getAllCategories'))
    else:
        category = get_category(cat_id)
        return render_template('deletecategory.html',category=category)

if __name__ == '__main__':
    app.secret_key = 'TODO_GETFROMFILE'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
