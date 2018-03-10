"""
This file stores the command db functions
to access the database with the app.
"""
from sqlalchemy import exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import BASE, Item, Category

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
ses = DBSession()


# db update function
def update_object(object_name):
    """
    Take and object, and update it in the database
    """
    try:
        ses.add(object_name)
        ses.commit()
    except exc.DatabaseError as e:
        print("Problem commiting the update in %s" % object_name.name)
        print("Error message:" % e.message)

# Print out all the categories
def list_all_category():
    """
    List all categories by name and id, order based on data table
    """
    
    category_list = ses.query(Category)

    for category in category_list:
        print("Name: {}, ID: {}".format(str(category.name), str(category.cat_id)))


def get_all_categories():
    """
    Get all categories by name and id, order based on data table
    Returns: An iterable list of category objects
    """
    
    return ses.query(Category)


# Find category by ID
def get_category(id_to_find):
    """ Using and id number, return category object """

    category = ses.query(Category).filter_by(id=id_to_find).one()
    return category


# Add a new category
def add_category(category_name):
    """

    """

    category = Category(name=category_name)
    ses.add(category)
    ses.commit()
    new_category = \
        ses.query(Category).filter_by(name=category_name).one()
    return new_category.id


# Delete a category
def delete_category(cat_id):
    """

    """
    category = get_category(cat_id)
    ses.delete(category)
    ses.commit()


# Change a category
def update_category(cat_id, name):
    """using an id, update the details of a category

    Args:
    cat_id - (int) id from the category table, for the
             category being changed.
    name - (string) New Name of the category.
    """
    category = get_category(cat_id)
    category.name = name
    update_object(category)

def get_all_items(cat_id):
    """ Using an ID, return a  item

    Args:
    cat_id - (int) id from the category table, for which
              to return
    Returns:
    List of (Object.Item)  item objects
    """

    items = ses.query(Item).filter_by(cat_id=cat_id)
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

    item = Item(name=name, price=price, \
        cat_id=cat_id, description=description)
    ses.add(item)
    ses.commit()
    new_item = \
        ses.query(Item).filter_by(name=name, cat_id=cat_id).one()
    return new_item.cat_id


def delete_item(cat_id):
    # Delete a item using an id
    item = get_item(cat_id)

    ses.delete(item)
    ses.commit()


def update_item(cat_id, item_id, name, description, price):
    """using an id, update the details of a item"""

    item = get_item(item_id)
    if str(name) != "":
        item.name = str(name)
    if str(description) != "":
        item.description = str(description)
    if str(price) != "":
        item.price = str(price)

    update_object(item)


# Return all the categories
def get_all_categories():
    """
    Get all categories by name and id, order based on data table
    Returns: An iterable list of category objects
    """
    
    return ses.query(Category)






