from flask import Flask, url_for, render_template, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import BASE, User, Item, Category
from db_command import *
# from categories_views import *
import pdb
# user auth libraries

from flask.ext.httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()


app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@auth.verify_password
def verify_password(usernameOrToken,password):
    # first see if the usernameOrToken is a token
    # if it is, it will pass back and ID, if not
    # it will send back None
    user_id = User.verify_auth_token(usernameOrToken)
    if user_id:
        print("Looking for user_id {0}".format(user_id))
        user = session.query(User).filter_by(id=user_id).first()
    else:
        print("Looking for user {0} with password {1}".format(usernameOrToken,password))
        user = session.query(User).filter_by(username=usernameOrToken).first()    
        if not user or not user.verify_password(password):
            return False

    g.user = user
    return True


#add /token route here to get a token for a user with login credentials
@app.route('/token', methods = ['GET'])
@auth.login_required
def get_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii')})#, 201#, {'Location': url_for('get_user', id = user.id, _external = True)}




@app.route('/')
@app.route('/categories')
def index():
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
def newItem(cat_id):

    if request.method == 'POST':
        new_id = add_item(cat_id,request.form['name'],request.form['description'],request.form['price'])
        flash("New item created!")
        return redirect(url_for('categoryItems', cat_id=cat_id))
    else:
        return render_template('new_category_item.html',cat_id=cat_id)

@app.route('/category/<int:cat_id>/category_items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(cat_id, item_id):
    # return "page to edit a category_items item. Task 2 complete!"
    if request.method == 'POST':
        update_item(cat_id,item_id, request.form['name'], request.form['description'], request.form['price'])
        flash("Item updated!")
        return redirect(url_for('categoryItems', cat_id=cat_id))
    else:
        item = get_item(item_id)
        return render_template('edititem.html',item=item)

@app.route('/category/<int:cat_id>/category_items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(cat_id, item_id):
    
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
    if request.method == 'POST':
        new_id = add_category(request.form['name'])
        flash("Category added!")
        return redirect(url_for('getAllCategories'))
    else:
        return render_template('newcategory.html')

@app.route('/category/<int:cat_id>/edit', methods=['GET', 'POST'])
def editCategory(cat_id):
    if request.method == 'POST':
        update_category(cat_id, request.form['name'])
        flash("Category updated!")
        return redirect(url_for('getAllCategories'))
    else:
        category = get_category(cat_id)
        return render_template('editcategory.html',category=category)

@app.route('/category/<int:cat_id>/delete', methods=['GET','POST'])
def deleteCategory(cat_id):

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
