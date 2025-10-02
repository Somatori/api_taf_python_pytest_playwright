import pytest
from tests.utils import safe_json, pretty_resp, assert_ok

@pytest.mark.usefixtures("auth_token")
def test_add_contact(api_client, contact_resource, auth_token):
    """
    Add Contact — verifies the contact created by the contact_resource fixture.
    The fixture creates the contact and will clean it up in teardown.
    This test performs full payload assertions (including street2) and checks server fields.
    """
    cid = contact_resource["id"]
    payload = contact_resource["payload"]

    # GET the created contact and assert full payload
    resp = api_client.get(f"/contacts/{cid}", token=auth_token)
    if resp.status != 200:
        pretty_resp(resp)
        pytest.fail(f"Expected GET 200 for created contact, got {resp.status}")

    body = safe_json(resp)
    assert body is not None, "Response body is not valid JSON"

    # Fields we expect to be echoed back exactly
    expected_fields = (
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
    )

    for field in expected_fields:
        assert field in body, f"Missing field '{field}' in response"
        assert body[field] == payload[field], (
            f"Field '{field}' mismatch: expected {payload[field]!r}, got {body[field]!r}"
        )

    # server-generated fields
    assert "_id" in body and isinstance(body.get("_id"), str)
    assert "owner" in body and isinstance(body.get("owner"), str)
    if "__v" in body:
        assert isinstance(body.get("__v"), int)
