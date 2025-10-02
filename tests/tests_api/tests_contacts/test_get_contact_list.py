import pytest
from tests.utils import safe_json, pretty_resp, assert_ok
from tests.tests_api.helpers.list_search import find_in_contacts_list


@pytest.mark.usefixtures("auth_token")
def test_get_contact_list(api_client, contact_resource, auth_token):
    """
    GET /contacts — confirm the created contact appears in the list (bounded pagination).
    """
    payload = contact_resource["payload"]
    cid = contact_resource["id"]

    # Quick sanity: GET by id should work
    get_resp = api_client.get(f"/contacts/{cid}", token=auth_token)
    assert_ok(get_resp)

    # Now search in list (bounded pages)
    found = find_in_contacts_list(api_client, auth_token, created_id=cid, email=payload["email"], page_size=100, max_pages=10)
    assert found is not None, "Created contact not found in first pages of contacts list"

    # Full payload assertions for the found item
    for field in (
        "firstName","lastName","birthdate","email","phone","street1","street2","city","stateProvince","postalCode","country",
    ):
        assert field in found, f"Missing field {field} in found list item"
        assert found[field] == payload[field], f"Field {field} mismatch"