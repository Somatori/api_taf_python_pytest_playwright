import pytest
from tests.factories import generate_contact_payload
from tests.utils import safe_json, pretty_resp, assert_ok

@pytest.mark.usefixtures("auth_token")
def test_get_contact(api_client, auth_token):
    """
    Happy-path test for GET /contacts/{contactId}.

    Flow:
      1) Create a contact (POST /contacts)
      2) GET the same contact by id and assert the response contains the expected fields
         (firstName, lastName, birthdate, email, phone, street1, city, stateProvince, postalCode, country)
      3) Verify server-generated fields (_id, owner, __v)
      4) Cleanup (DELETE the created contact) in finally
    """
    created_id = None
    payload = generate_contact_payload()

    # 1) Create the contact
    create_resp = api_client.post("/contacts", token=auth_token, json=payload)
    assert_ok(create_resp)

    create_body = safe_json(create_resp)
    assert create_body is not None, "Create response body is not valid JSON"

    created_id = create_body.get("_id")
    assert created_id, f"Create response did not contain an id: {create_body}"

    try:
        # 2) GET the created contact
        get_resp = api_client.get(f"/contacts/{created_id}", token=auth_token)
        if get_resp.status != 200:
            pretty_resp(get_resp)
            pytest.fail(f"Expected GET status 200, got {get_resp.status}")

        body = safe_json(get_resp)
        assert body is not None, "GET response body is not valid JSON"

        # 3) Full payload assertions (fields from the example)
        expected_fields = (
            "firstName",
            "lastName",
            "birthdate",
            "email",
            "phone",
            "street1",
            "city",
            "stateProvince",
            "postalCode",
            "country",
        )

        for field in expected_fields:
            assert field in body, f"Missing field '{field}' in GET response"
            assert body[field] == payload[field], (
                f"Field '{field}' mismatch: expected {payload[field]!r}, got {body[field]!r}"
            )

        # Server-generated fields
        assert "_id" in body, "Response missing '_id'"
        assert isinstance(body.get("_id"), str)

        assert "owner" in body, "Response missing 'owner'"
        assert isinstance(body.get("owner"), str)

        if "__v" in body:
            assert isinstance(body.get("__v"), int)

    finally:
        # Cleanup: try to delete the created contact (best-effort)
        if created_id:
            try:
                _ = api_client.delete(f"/contacts/{created_id}", token=auth_token)
            except Exception as e:
                print(f"Warning: cleanup failed for contact {created_id}: {e}")
