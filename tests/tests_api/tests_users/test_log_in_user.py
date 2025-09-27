# tests/tests_api/tests_users/test_log_in_user.py
import pytest
from tests.config import TEST_USER_EMAIL, TEST_USER_PASS
from tests.utils import assert_ok, safe_json


def test_log_in_user(api_client):
    """
    Happy-path test for POST /users/login.
    - Requires TEST_USER_EMAIL and TEST_USER_PASS to be set in .env.
    - Asserts that the response contains a non-empty token and a `user` object
      which includes _id, firstName, lastName, email (and optional __v).
    """
    email = TEST_USER_EMAIL
    password = TEST_USER_PASS

    if not email or not password:
        pytest.skip(
            "TEST_USER_EMAIL and TEST_USER_PASS are not set in .env — "
            "this API requires pre-registered credentials. Add them to .env to run this test."
        )

    resp = api_client.post("/users/login", json={"email": email, "password": password})
    # Accept any 2xx (some APIs return 200)
    assert_ok(resp)

    body = safe_json(resp)
    assert body is not None, "Response body is not valid JSON"

    # Top-level token
    assert "token" in body, f"No token found in response: {body}"
    token = body["token"]
    assert isinstance(token, str) and len(token) > 8, "Token is missing or too short"

    # User object checks
    assert "user" in body and isinstance(body["user"], dict), f"Missing or invalid 'user' object: {body}"
    user = body["user"]

    # Required user fields
    required_fields = ("_id", "firstName", "lastName", "email")
    for f in required_fields:
        assert f in user, f"Missing field '{f}' in user object: {user}"

    # email should match the login email
    assert user.get("email") == email, f"Returned user email {user.get('email')!r} does not match login email {email!r}"

    # types sanity checks
    assert isinstance(user.get("_id"), str)
    assert isinstance(user.get("firstName"), str)
    assert isinstance(user.get("lastName"), str)

    # optional __v (version) check if present
    if "__v" in user:
        assert isinstance(user.get("__v"), int)
