
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
        token = "this should be a problem"
        User.verify_auth_token(token)

    seconds_to_allow = 1
    token = u.generate_auth_token(seconds_to_allow)
    print(len(token))
    assert len(token) == 132

    decoded_token_user_id = u.verify_auth_token(token)
    print(decoded_token_user_id)
    assert decoded_token_user_id == 9999

    # assert that the decode can happen more than once
    # with the same token
    decoded_token_user_id2 = u.verify_auth_token(token)
    print(decoded_token_user_id2)
    assert decoded_token_user_id2 == 9999

    # expire
    sleep(seconds_to_allow + 1)
    decoded_token_user_id = u.verify_auth_token(token)
    print(decoded_token_user_id)
    assert decoded_token_user_id == None

    
def test_token_decode_error():
    # junk for blank data sent to be decoded.
    # give an a user
    # when the verify auth token is passed an empty string
    # then None should be returned
    u = User()
    u.email = "test@example.com"
    u.id = 9999
    u.username = "tester"
    u.password_hash = fixture_string_generate(64)
    token = ""
    with raises(Exception) as e_info:
        _ = User.verify_auth_token(token)



