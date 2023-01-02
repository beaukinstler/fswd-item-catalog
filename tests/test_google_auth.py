import pytest
import json
from main_app import SUPER_SECRET_KEY, GOOG_CLIENT_ID, gconnect

import google_auth as ga


class TestGroup:
    """
    given:
    when:
    then:
    """

    @pytest.fixture
    def fixture_goog_data(self):
        data = (
            json.loads(
                    open("tests/fixture_data/converted_goog_token.json",
                        'r').read()
                )
        )
        return data

    @pytest.fixture
    def fixture_user(self):
        data = {
                    "email":"email@example.com",
                    "sub":"12345678912312345678",
            }
        return data

    def test_fixture_goog_data(self,fixture_goog_data):
        email = fixture_goog_data.get("email")
        assert "@" in email

    def test_new_auth(self):
        with pytest.raises(Exception) as e_info:
            dir(ga)
            1/0

    def test_get_credential(self):
        assert len(GOOG_CLIENT_ID) > 10

    def test_validate_user(self, fixture_goog_data, fixture_user):

        user_is_valid = ga.validate_user(
                                fixture_goog_data,
                                fixture_user
                            )
        assert user_is_valid == True







