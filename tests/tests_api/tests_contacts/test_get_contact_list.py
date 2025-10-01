import pytest
from tests.factories import generate_contact_payload
from tests.utils import safe_json, pretty_resp, assert_ok

EXPECTED_FIELDS = (
    "_id",
    "firstName",
    "lastName",
    "birthdate",
    "email",
    "phone",
    "street1",
    # "street2" may be present
    "city",
    "stateProvince",
    "postalCode",
    "country",
    "owner",
    "__v",
)


@pytest.mark.usefixtures("auth_token")
def test_get_contact_list(api_client, auth_token):
    """
    Happy-path test for GET /contacts (Get Contact List).

    Flow:
      1) Create a contact (POST /contacts)
      2) GET /contacts and assert response is a list
      3) For each item in list assert expected fields exist and types are sane
      4) Find created contact in the list and assert all its fields match the payload
      5) Cleanup: delete created contact
    """
    created_id = None
    payload = generate_contact_payload()

    # 1) Create a contact
    create_resp = api_client.post("/contacts", token=auth_token, json=payload)
    assert_ok(create_resp)

    create_body = safe_json(create_resp)
    assert create_body is not None, "Create response body is not valid JSON"
    created_id = create_body.get("_id")
    assert created_id, f"Create response did not return an id: {create_body}"

    try:
        # 2) GET list
        list_resp = api_client.get("/contacts", token=auth_token)
        if list_resp.status != 200:
            pretty_resp(list_resp)
            pytest.fail(f"Expected GET /contacts status 200, got {list_resp.status}")

        list_body = safe_json(list_resp)
        assert isinstance(list_body, list), f"Expected response to be a list, got {type(list_body).__name__}"

        # 3) Basic checks for each item (presence & basic types)
        for idx, item in enumerate(list_body):
            # each item must be a dict
            assert isinstance(item, dict), f"Contact list item at index {idx} is not an object: {item!r}"

            # required fields presence
            for f in EXPECTED_FIELDS:
                # __v and street2 may be optional on some records; only check if present
                if f not in item:
                    # allow missing street2 or __v, but require the rest
                    if f in ("street2", "__v"):
                        continue
                    pytest.fail(f"Missing expected field '{f}' in contacts list item: {item}")

            # basic type checks for a few fields
            if "_id" in item:
                assert isinstance(item["_id"], str)
            if "email" in item:
                assert isinstance(item["email"], str)
            if "firstName" in item:
                assert isinstance(item["firstName"], str)

        # 4) Find the created contact in list and assert it matches payload exactly (for the fields we sent)
        found = None
        for item in list_body:
            if (item.get("_id") == created_id) or (item.get("email") == payload["email"]):
                found = item
                break

        assert found is not None, f"Created contact (id={created_id}) not found in contacts list"

        # For the found item, assert all fields match the payload (including optional street2)
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
            # If payload included the field, it must be present and equal in the response item
            expected_val = payload.get(field)
            # treat None as absence for street2 if generate_contact_payload doesn't include it
            if expected_val is None:
                # If payload didn't set street2, it's okay that the returned item has it or not;
                # but if the server returns a field, just ensure it's a string.
                if field in found:
                    assert isinstance(found[field], (str, type(None)))
                continue

            assert field in found, f"Field '{field}' missing in found contact: {found}"
            assert found[field] == expected_val, (
                f"Field '{field}' mismatch for created contact: expected {expected_val!r}, got {found[field]!r}"
            )

    finally:
        # 5) Cleanup: delete created contact (best-effort)
        if created_id:
            try:
                _ = api_client.delete(f"/contacts/{created_id}", token=auth_token)
            except Exception as e:
                print(f"Warning: cleanup failed for contact {created_id}: {e}")
