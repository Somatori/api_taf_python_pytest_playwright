# tests/tests_api/tests_users/test_log_in_user.py
import json
from pathlib import Path
import pytest
from jsonschema import validate, ValidationError

from tests.config import TEST_USER_EMAIL, TEST_USER_PASS
from tests.utils import assert_ok, safe_json, pretty_resp

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "login_schema.json"


def load_schema(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_log_in_user_schema(api_client):
    """
    Happy-path test for POST /users/login with JSON Schema validation.
    - Requires TEST_USER_EMAIL and TEST_USER_PASS in .env.
    - Validates the response structure against tests/tests_api/schemas/login_schema.json.
    """
    email = TEST_USER_EMAIL
    password = TEST_USER_PASS

    if not email or not password:
        pytest.skip(
            "TEST_USER_EMAIL and TEST_USER_PASS are not set in .env — "
            "this API requires pre-registered credentials. Add them to .env to run this test."
        )

    resp = api_client.post("/users/login", json={"email": email, "password": password})
    assert_ok(resp)

    body = safe_json(resp)
    assert body is not None, "Response body is not valid JSON"

    # load schema and validate
    schema = load_schema(SCHEMA_PATH)
    try:
        validate(instance=body, schema=schema)
    except ValidationError as e:
        # Print helpful debug output and fail the test with the schema error message
        pretty_resp(resp)
        pytest.fail(f"Response JSON does not match schema: {e.message}\nValidator path: {list(e.path)}\nSchema path: {list(e.schema_path)}")

    # extra sanity checks
    token = body.get("token")
    assert isinstance(token, str) and len(token) > 8
    user = body.get("user")
    assert user.get("email") == email
