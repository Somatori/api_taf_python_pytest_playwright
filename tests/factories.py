"""
Test data factories for API tests.
Provides generate_contact_payload() which returns a dict matching the
contact POST body used by the Contact List API.

Usage:
    payload = generate_contact_payload()
    payload = generate_contact_payload(overrides={"firstName": "Alice"})
"""
from datetime import date, timedelta
import random
import uuid


def _random_birthdate(start_year=1950, end_year=2000):
    """Return a birthdate string YYYY-MM-DD between start_year and end_year."""
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta_days = (end - start).days
    chosen = start + timedelta(days=random.randint(0, delta_days))
    return chosen.isoformat()


def _unique_local_part():
    """Generate a short unique local-part for an email address."""
    return f"test{uuid.uuid4().hex[:8]}"


def generate_contact_payload(overrides: dict = None) -> dict:
    """
    Generate a contact payload matching the API expected schema.
    Pass `overrides` to replace any default values.
    """
    overrides = overrides or {}

    uid = _unique_local_part()
    payload = {
        "firstName": f"Test{uid}",
        "lastName": "User",
        "birthdate": _random_birthdate(1950, 2000),
        "email": f"{uid}@example.com",
        "phone": "8005555555",
        "street1": "1 Main St.",
        "street2": "Apartment A",
        "city": "Anytown",
        "stateProvince": "KS",
        "postalCode": "12345",
        "country": "USA",
    }

    # Apply overrides (simple shallow merge)
    payload.update(overrides)
    return payload
