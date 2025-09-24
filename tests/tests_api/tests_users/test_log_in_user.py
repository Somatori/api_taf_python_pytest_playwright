import pytest
from tests.config import TEST_USER_EMAIL, TEST_USER_PASS

def test_log_in_user(api_client):
    """
    Happy-path test for POST /users/login.
    - Requires TEST_USER_EMAIL and TEST_USER_PASS to be set in .env.
    - Does NOT attempt to register a user because the API requires a token for user creation.
    - Asserts that a non-empty token string is returned on successful login.
    """
    email = TEST_USER_EMAIL
    password = TEST_USER_PASS

    if not email or not password:
        pytest.skip(
            "TEST_USER_EMAIL and TEST_USER_PASS are not set in .env — "
            "this API requires pre-registered credentials. Add them to .env to run this test."
        )

    token = api_client.login_user(email, password)
    assert token, "Login did not return a token (check credentials in .env and the API availability)"
    assert isinstance(token, str) and len(token) > 8
