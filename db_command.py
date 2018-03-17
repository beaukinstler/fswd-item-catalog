"""
This file stores the command db functions
to access the database with the app.
"""
from sqlalchemy import exc, desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import string
from db_setup import BASE, Item, Category, User

engine = create_engine('sqlite:///catalog.db')

BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

ses = DBSession()


def update_object(object_name):
    """
    Purpose:
            Take and object, and update it in the database
            Reduce code by allowing this generic update to
            commit any session object to the db.
    Args:
            (Object) Takes a record object

    Exceptions:
            Catches and prints DatabaseError exceptions
    """
    try:
        ses.add(object_name)
        ses.commit()
    except exc.DatabaseError as e:
        print("Problem commiting the update in %s" % object_name.name)
        print("Error message:" % e.message)


def list_all_category():
    """
    List all categories by name and id, order based on data table
    """

    category_list = ses.query(Category)

    for category in category_list:
        print("Name: {0}, ID: {1}".format(str(category.name),
                                          str(category.cat_id)))


def get_all_categories():
    """
    Get all categories by name and id, order based on data table
    Returns: An iterable list of category objects
    """

    return ses.query(Category)


# Find category by ID
def get_category(id_to_find):
    """ Using and id number, return a category object """

    category = ses.query(Category).filter_by(id=id_to_find).one()
    return category


# Add a new category
def add_category(category_name):
    """
    Create a category in the database

    Args: category_name - String(80)

    Returns: category.id - Int
    """

    category = Category(name=category_name)
    ses.add(category)
    ses.commit()
    new_category = ses.query(Category).filter_by(name=category_name).one()
    return new_category.id


def delete_category(cat_id):
    """
    Using an id, delete a category from the database

    Args: cat_id - Int
    """
    category = get_category(cat_id)
    ses.delete(category)
    ses.commit()


# Change a category
def update_category(cat_id, name):
    """
    Using an id, update the details of a category

    Args:
    cat_id - (int) id from the category table, for the
             category being changed.
    name - (string) New Name of the category.
    """
    category = get_category(cat_id)
    category.name = name
    update_object(category)


def get_all_items(cat_id=0):
    """
    Using an category.id, return all items in that category

    Args:
    cat_id - (int) id from the category table to return

    Returns:
    List of (Object.Item)  item objects
    """
    if cat_id == 0:
        items = ses.query(Item)
    else:
        items = ses.query(Item).filter_by(cat_id=cat_id)
    return items


def get_recent_items(cat_id=0, limit_number=10):
    """
    Return a list of recent items

    Args:
    cat_id[optional] - (int) id from the category table, for which
              to return
    limit_number[optional] - defaults to 10

    Returns:
    List of (Object.Item) most recent added to db based
    on the id number.
    """
    if cat_id == 0:
        items = ses.query(Item).order_by(desc(Item.id)).limit(limit_number)
    else:
        items = (
                ses.query(Item).filter_by(cat_id=cat_id)
                .order_by(desc(Item.id)).limit(limit_number)
            )
    return items


def get_item(id_to_find):
    """ Using an ID, return a  item

    Args:
    cat_id - (int) id from the category table, for the
             category being changed.
    name - (string) New Name of the category.

    Returns:
    (Object.Item)  item object
    """

    item = ses.query(Item).filter_by(id=id_to_find).one()
    return item


def add_item(cat_id, name, description, price=0):
    """
    Using an id and a category, add a  item

    Args:
    cat_id - (int) id from the category table, for the
             being added to.
    name - (string) name of the item
    price - (string) price of the item, no leading '$'

    Returns:
    id - (int) Id of the new item
    """

    item = (
            Item(
                name=name, price=price,
                cat_id=cat_id,
                description=description
                )
        )
    new_id = ses.add(item)
    print(new_id)
    ses.commit()
    new_item = (
            ses.query(Item).filter_by(name=name, cat_id=cat_id).first()
        )
    return new_item.id


def delete_item(item_id):
    """
    Using an id, delete an item from the database

    Args: item_id - Int
    """
    item = get_item(item_id)
    ses.delete(item)
    ses.commit()


def update_item(cat_id, item_id, name, description, price):
    """
    using an id, update the details of a item
    item id cannot be updated. If a detail is blank, it will be skipped

    Args:
        cat_id: Int-id of the category to set for the item
        item_id: Int(primary_key)will be used to lookup the item from the table
        name: String(80) Name to set the item to
        price: String(8) Price of the item
    """

    item = get_item(item_id)
    if str(name) != "":
        item.name = str(name)
    if str(description) != "":
        item.description = str(description)
    if str(price) != "":
        item.price = str(price)
    if str(cat_id) != "":
        item.cat_id = str(cat_id)

    update_object(item)


def get_all_categories():
    """
    Get all categories by name and id, order based on data table
    Returns: An iterable list of category objects
    """
    return ses.query(Category)


def get_user(username):
    # first look up the username
    user = ses.query(User).filter_by(username=username).first()

    # next look in the email field, in case email was used instead
    if user is None:
        user = ses.query(User).filter_by(email=username).first()
    return user


def get_user_from_id(id):
    user = ses.query(User).filter_by(id=id).first()
    return user


def get_user_id_from_email(email):
    try:
        user = ses.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


def get_user_from_email(email):
    try:
        user = ses.query(User).filter_by(email=email).first()
        return user
    except:
        return None


def add_user(username, password, email):
    """
    Add a new user, return None if not able
    """

    if ses.query(User).filter_by(username=username).first() is None:
        new_user = User(username=username, email=email)
        new_user.hash_password(password)
        # new_user.active = 0
        ses.add(new_user)
        ses.commit()
        return get_user(username).id
    else:
        return None


def update_user(username, password, email):
    """
    Add a new user, return None if not able
    """
    user = get_user(username) if get_user(username) is not None else get_user(email)  # noqa
    if user is not None:
        if str(username) != '':
            user.username = str(username)
        if str(email) != '':
            user.email = str(email)
        if str(password) != '':
            user.hash_password(password)

        ses.add(user)
        ses.commit()
        return get_user(username).id
    else:
        return None


def get_all_users():
    return ses.query(User)


def createUser(login_session):
    """
    Create an OAuth user, with a fake password hash
    Args: web session object
    Returns: userID (int)
    """
    fake_password_hash = (
            ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for x in xrange(255)  # noqa
                )
        )
    newUser = (
            User(
                    username=login_session['username'],
                    email=login_session['email'],
                    password_hash=fake_password_hash
                )
        )
    ses.add(newUser)
    ses.commit()
    user = ses.query(User).filter_by(email=login_session['email']).one()
    return user.id
