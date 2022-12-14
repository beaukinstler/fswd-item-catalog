
from pytest import raises
from time import sleep

"""
in the current form, the file db_setup.py is 
executing code. So, instead of importing that full file,
am replicating its imports, and importing just the 
classes
Also creating a BASE, and ENGINE 
uniqe to the test.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as app_context
import random
import string
from itsdangerous import(
        BadSignature,
        SignatureExpired
    )


BASE = declarative_base()

# This secret_key will be used to both encrypt and decrypt
"""
this code is used in the setup.

secret_key = (
        ''.join(random.choice(
                string.ascii_uppercase + string.digits) for _ in range(32)
                )
    )
"""


"""
all of these apear to inherit from the BASE object 
it's a SQLAlchemy object.
"""
from db_setup import User, Category, Item

def fixture_string_generate(qty:int = 32):
    chars = string.ascii_uppercase
    nums = string.digits
    return "".join(list((random.choice(chars+nums) for _ in range(qty) )))

def test_creating_key():

    thirty_two_chars = fixture_string_generate(32)
    print(thirty_two_chars)

    assert len(thirty_two_chars) == 32


def test_make_user():
    u = User()
    u.email = "test@example.com"
    u.id = 9999
    u.username = "tester"
    u.password_hash = fixture_string_generate(64)
    with raises(Exception) as e_info:
        token = {"token":"test"}
        User.verify_auth_token(token)

    
    token = u.generate_auth_token(10)
    print(len(token))
    assert len(token) == 132

    decoded_token_user_id = u.verify_auth_token(token)
    print(decoded_token_user_id)
    assert decoded_token_user_id == 9999







# ENGINE = create_engine('sqlite:///test_catalog.db')

# BASE.metadata.create_all(ENGINE)