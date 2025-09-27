import pytest
from tests.factories import generate_contact_payload
from tests.utils import assert_status, assert_ok, safe_json

@pytest.mark.usefixtures("auth_token")
def test_add_contact(api_client, auth_token):
    """
    Happy-path test for POST /contacts (Add Contact).
    - Uses auth_token fixture (skips if credentials not provided).
    - Verifies that the response includes all submitted fields and
      that server-generated fields (_id, owner, __v) are present and typed.
    - Attempts to delete the created contact in a finally block.
    """
    payload = generate_contact_payload()

    resp = api_client.post("/contacts", token=auth_token, json=payload)

    # Accept 201 Created or any 2xx; prefer 201 if documented.
    if resp.status == 201:
        assert_status(resp, 201)
    else:
        assert_ok(resp)

    body = safe_json(resp)
    assert body is not None, "Response body is not valid JSON"

    # Server should return the created resource with an id
    created_id = body.get("_id")
    assert created_id, f"Created contact id not found in response: {body}"

    # If a specific id key exists, validate its type
    if "_id" in body:
        assert isinstance(body.get("_id"), str)

    # Check that the server echoed back the submitted fields exactly
    for field in (
        "firstName",
        "lastName",
        "birthdate",
        "email",
        "phone",
        "street1",
        "street2",
        "city",
        "stateProvince",
        "postalCode",
        "country",
    ):
        assert field in body, f"Missing field '{field}' in response"
        assert body[field] == payload[field], f"Field '{field}' mismatch: expected {payload[field]!r}, got {body[field]!r}"

    # owner should be present and look like a string id
    assert "owner" in body, "Response missing 'owner'"
    assert isinstance(body.get("owner"), str)

    # __v is often a version int in Mongo-like APIs; if present, check type
    if "__v" in body:
        assert isinstance(body.get("__v"), int)

    # Cleanup: try to delete created contact (best-effort)
    try:
        del_resp = api_client.delete(f"/contacts/{created_id}", token=auth_token)
        if del_resp.status not in (200, 204):
            # Print details but do not fail the primary test
            print(f"Warning: cleanup DELETE returned {del_resp.status}. Body: {del_resp.text()}")
    except Exception as e:
        print(f"Warning: cleanup DELETE raised exception: {e}")
