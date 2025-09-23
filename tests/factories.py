# tests/factories.py
import uuid

def generate_contact_payload():
    uid = uuid.uuid4().hex[:8]
    return {
        "firstName": f"Test{uid}",
        "lastName": "User",
        "email": f"test{uid}@example.com",
        "phone": "555-0101"
    }
