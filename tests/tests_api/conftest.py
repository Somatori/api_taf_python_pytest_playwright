import os
from pathlib import Path
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from .clients.api_client import ApiClient


# Load root .env
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

API_BASE_URL = os.getenv("API_BASE_URL", "https://thinking-tester-contact-list.herokuapp.com")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL")
TEST_USER_PASS = os.getenv("TEST_USER_PASS")


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
            "Content-Type": "application/json",
        }
    )
    yield ctx
    ctx.dispose()


@pytest.fixture(scope="session")
def auth_token(api_request_context):
    """
    A simple session-scoped auth token fixture.
    Priority:
      1) If TEST_USER_EMAIL and TEST_USER_PASS are set in .env -> login and return token
      2) Otherwise return None (tests can create ephemeral users as needed)
    """
    email = TEST_USER_EMAIL
    pwd = TEST_USER_PASS
    if not email or not pwd:
        return None

    resp = api_request_context.post("/users/login", json={"email": email, "password": pwd})
    try:
        body = resp.json()
    except Exception:
        body = {}

    if resp.ok:
        # token field names vary by API; try common keys
        for key in ("token", "accessToken", "access_token", "auth_token"):
            if key in body:
                return body[key]
        # Fallback: if body contains 'user' with token
        if isinstance(body.get("user"), dict):
            for key in ("token", "accessToken", "access_token", "auth_token"):
                if key in body["user"]:
                    return body["user"][key]
    # If login failed or token not found, return None (tests should handle None)
    return None


@pytest.fixture
def api_client(api_request_context):
    """
    Provide a thin ApiClient wrapper around Playwright's APIRequestContext.
    Function-scoped by default for safety/isolation.
    """
    return ApiClient(api_request_context)

