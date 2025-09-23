# General fixtures that apply to the whole tests/ tree can live here.
# API-specific fixtures are under tests/tests_api/conftest.py

import logging
import pytest

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    yield
