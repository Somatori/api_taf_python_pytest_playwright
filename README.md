# api_taf_python_pytest_playwright
The initial API test automation framework (Python / Pytest / Playwright)

## Quick start

1. Create & activate virtual environment (macOS / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip and install dependencies:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

3. Copy `.env.template` to `.env` and fill required values (especially if you want authenticated tests):

```bash
cp .env.template .env
# edit .env to include API_BASE_URL, TEST_USER_EMAIL, TEST_USER_PASS as needed
```

4. Create the reports folder if it does not exist:

```bash
mkdir -p reports
```

---

## Reporting (html)
This project uses **pytest-html** to produce a single-file HTML report after each pytest run. The generated report is placed in the `reports/` directory (default `reports/report.html`).

### How reporting is configured
- `pytest.ini` includes an `addopts` line that runs pytest with `--html=reports/report.html --self-contained-html` so a report is produced automatically whenever you run `pytest`.
- You can disable the automatic generation by removing the `addopts` from `pytest.ini` and instead run pytest with the `--html` option manually when you want a report.



Notes:
- This repo uses Playwright's APIRequestContext (sync API) for HTTP calls.
- Browser engines are not required for API-only tests. If you later add web tests, run:
  playwright install
