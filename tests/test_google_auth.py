import pytest
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
        return ""

    def test_new_auth(self):
        with pytest.raises(Exception) as e_info:
            dir(ga)
            1/0

    def test_get_credential(self):
        assert len(GOOG_CLIENT_ID) > 10





    


