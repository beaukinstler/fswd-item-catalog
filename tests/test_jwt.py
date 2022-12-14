import jwt
from pytest import raises
from datetime import datetime, timedelta, timezone
from time import sleep


plaintext = "a long time ago in a..."
key = "secret"
# establish a fiture expiration
seconds_to_test = 1
goodfor = timedelta(0,seconds_to_test) # days: 0, seconds: var
future_time =  datetime.now(tz=timezone.utc) + goodfor

# build the data with new time for expiring
dict_data = {"token": plaintext, "exp":future_time}
# encode and decode the new data
encoded = jwt.encode(dict_data, key, algorithm="HS256")


def test_valid_time():
    decoded = jwt.decode(encoded, key, algorithms="HS256")
    assert decoded['token'] == plaintext


def test_encode_of_simple_string_fails():
    with raises(Exception) as e_info:
        _ = jwt.encode(plaintext, "some secret", algorithm="HS256")


def test_encode_of_simple_dict_no_time_limit():
    simple_data = {"token": plaintext}
    encoded = jwt.encode(simple_data, "some secret", algorithm="HS256")
    unencoded = jwt.decode(encoded, "some secret", algorithms="HS256")

    assert unencoded['token'] == plaintext

def test_expired_time():
    # sleep until expired and assume and exception will be thrown
    # time and token created globally.
    # see the setup above.

    sleep(seconds_to_test + 1 )

    # time shoud have expired by now.
    with raises(Exception) as e_info:
        unencoded = jwt.decode(encoded, key, algorithms="HS256")

