# tests/tests_api/conftest.py
import os
from pathlib import Path
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load root .env
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

API_BASE_URL = os.getenv("API_BASE_URL", "https://thinking-tester-contact-list.herokuapp.com")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL")
TEST_USER_PASS = os.getenv("TEST_USER_PASS")

# Relative import for ApiClient
from .clients.api_client import ApiClient


@pytest.fixture(scope="session")
def playwright_instance():
    """Start sync_playwright once per session."""
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def api_request_context(playwright_instance):
    """
    Provide a Playwright APIRequestContext for tests.
    Session-scoped for speed; change to function-scope for strict isolation.
    """
    ctx = playwright_instance.request.new_context(
        base_url=API_BASE_URL,
        extra_http_headers={
            "Accept": "application/json",
            # We typically set Content-Type per-request when sending json
        }
    )
    yield ctx
    ctx.dispose()


@pytest.fixture
def api_client(api_request_context):
    """
    Provide a thin ApiClient wrapper around Playwright's APIRequestContext.
    Function-scoped by default for safety/isolation.
    """
    return ApiClient(api_request_context)


@pytest.fixture(scope="session")
def auth_token(api_request_context):
    """
    Session-scoped fixture that logs in using TEST_USER_EMAIL/TEST_USER_PASS and
    returns a bearer token string for use in authenticated requests.

    - If TEST_USER_EMAIL / TEST_USER_PASS are not set, this fixture will skip tests that require auth.
    - If login fails (no token returned), the fixture will fail the session (pytest.fail).
    """
    email = TEST_USER_EMAIL
    pwd = TEST_USER_PASS

    if not email or not pwd:
        pytest.skip(
            "TEST_USER_EMAIL and TEST_USER_PASS are not set in .env — "
            "tests requiring authentication will be skipped. Add credentials to run authenticated tests."
        )

    client = ApiClient(api_request_context)
    token = client.login_user(email, pwd)

    if not token:
        pytest.fail(
            "Login attempt did not return a token. Check TEST_USER_EMAIL/TEST_USER_PASS in .env "
            "or verify the API's /users/login endpoint is available."
        )

    return token


@pytest.fixture
def auth_headers(auth_token):
    """Helper fixture returning the authorization header dict for use in requests."""
    return {"Authorization": f"Bearer {auth_token}"}
