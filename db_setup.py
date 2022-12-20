"""
This is a class to setup the data connections for a
item catalog with categories web application
"""
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as app_context
import random
import string
# from itsdangerous import(
#         # TimedJSONWebSignatureSerializer as Serializer,

#         BadSignature,
#         SignatureExpired
#     )
import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError
from datetime import datetime, timedelta, timezone

BASE = declarative_base()

# This secret_key will be used to both encrypt and decrypt
secret_key = (
        ''.join(random.choice(
                string.ascii_uppercase + string.digits) for x in range(32)
                )
    )


class User(BASE):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True, unique=True)
    password_hash = Column(String(64))
    email = Column(String(250), index=True, unique=True)
    # active = Column(Integer, default=0)

    def hash_password(self, password):
        self.password_hash = app_context.encrypt(password)

    def verify_password(self, password):
        return app_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        """
        Use jwt.encode
        to encrypt a token, and the secret key created global
        in the class.

        Parameters:
            self

            [optional]
            expiraexpiration: integer, seconds until expires

        Returns: encrypted token, containing id of the user
        """
        # s = Serializer(secret_key, expires_in=expiration)
        """replace the above code with jwt.encode"""
        # days: 0, seconds: var
        goodfor = timedelta(0,expiration)
        future_time =  datetime.now(tz=timezone.utc) + goodfor
        token = {'id': self.id}
        dict_data = {"token": token, "exp":future_time}
        encoded_token = jwt.encode(dict_data, secret_key, algorithm="HS256")
        return encoded_token

    @property
    def serialize(self):
        """Return the object fields as JSON like format"""
        return {
            'name': self.username,
            'id': self.id,
            'email': self.email
        }

    @staticmethod
    def verify_auth_token(token):
        """
        Purpose: Decrypt a token and check for the user id.
                 Exceptions are thrown for expired tokens,
                 and for BadSignatures. If these exceptions
                 are found, "None" is returned

        Params: A token created with jwt.encode

        Returns: a user_id if successfully decrypted
                 from the token
        """

        
        try:
            decoded_data = jwt.decode(token, secret_key, algorithms="HS256")
            print(str(decoded_data))
            data = decoded_data['token']
        except ExpiredSignatureError:
            print("Expired token")
            return None
        except InvalidSignatureError:
            print("Bad token: {0}".format(InvalidSignatureError.message))
            return None
        except DecodeError:
            print("Decoding error: {0}".format(DecodeError))
            return None
        except Exception as e:
            print("Unexpected exection")
            print
            print(type(e).__name__)
            raise e
       
        return data['id']


class Category(BASE):
    """
    Define category class
    Extends a constant of an instance of declarative_base()
    """

    __tablename__ = 'category'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    items = relationship("Item", cascade="delete, delete-orphan")

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        """Return the object fields as JSON like format"""
        return {
            'name': self.name,
            'id': self.id,
            'owner_username': self.user.username
        }


class Item(BASE):
    """
    Define category class
    Extends a constant of an instance of declarative_base()
    """

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))

    cat_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category, viewonly=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        """Return the object fields as JSON like format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'category': self.category.name,
            'category_id': self.cat_id,
            'owner_username': self.user.username
        }

ENGINE = create_engine('sqlite:///catalog.db')

BASE.metadata.create_all(ENGINE)
