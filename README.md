# api_taf_python_pytest_playwright
The initial API test automation framework (Python / Pytest / Playwright)

## Quick start

1. Create & activate venv:
   python3 -m venv .venv
   source .venv/bin/activate

2. Install dependencies:
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt

3. Copy .env.template -> .env and fill credentials:
   cp .env.template .env
   # edit .env to add TEST_USER_EMAIL and TEST_USER_PASS if you want a dedicated test user.

Notes:
- This repo uses Playwright's APIRequestContext (sync API) for HTTP calls.
- Browser engines are not required for API-only tests. If you later add web tests, run:
  playwright install
