from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

API_BASE_URL = os.getenv("API_BASE_URL", "https://thinking-tester-contact-list.herokuapp.com")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL")
TEST_USER_PASS = os.getenv("TEST_USER_PASS")
