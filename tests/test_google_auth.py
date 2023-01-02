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
    def fixture1(self):
        data = (
        json.loads(
            open("tests/fixture_data/converted_google_token.json", 'r')
            .read())
    )
        return data

    def test_fixture1(self,fixture1):
        email = fixture1.get("email")
        assert "@" in email

    def test_new_auth(self):
        with pytest.raises(Exception) as e_info:
            dir(ga)
            1/0

    def test_get_credential(self):
        assert len(GOOG_CLIENT_ID) > 10

    def test_validate_user(self, fixture1):
        assert ga.validate_user(fixture1, {"email":"beaukinstler@gmail.com"}) == True







