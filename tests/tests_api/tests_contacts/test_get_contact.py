import pytest
from tests.utils import safe_json, pretty_resp, assert_ok


@pytest.mark.usefixtures("auth_token")
def test_get_contact(api_client, contact_resource, auth_token):
    """
    GET /contacts/{id} — uses the contact_resource fixture that created the contact.

    Asserts full payload (including street2) and server-generated fields.
    """
    cid = contact_resource["id"]
    payload = contact_resource["payload"]

    # GET by id
    resp = api_client.get(f"/contacts/{cid}", token=auth_token)
    if resp.status != 200:
        pretty_resp(resp)
        pytest.fail(f"Expected GET 200, got {resp.status}")

    body = safe_json(resp)
    assert body is not None

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

    for f in expected_fields:
        assert f in body, f"Missing field {f} in GET response"
        assert body[f] == payload[f], f"Mismatch for field {f}: expected {payload[f]!r}, got {body[f]!r}"

    # server fields
    assert "_id" in body and isinstance(body.get("_id"), str)
    assert "owner" in body and isinstance(body.get("owner"), str)
    if "__v" in body:
        assert isinstance(body.get("__v"), int)