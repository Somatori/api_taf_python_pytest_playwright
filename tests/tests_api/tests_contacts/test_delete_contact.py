# tests/tests_api/tests_contacts/test_delete_contact.py
import pytest
from tests.factories import generate_contact_payload
from tests.utils import assert_ok, safe_json, pretty_resp

@pytest.mark.usefixtures("auth_token")
def test_delete_contact(api_client, auth_token):
    """
    Happy-path test for DELETE /contacts/{contactId} (Delete Contact).

    Flow:
      1) Create a contact (POST /contacts) — assert creation succeeded.
      2) DELETE the contact using the returned id — expect 200 OK and exact body "Contact deleted".
      3) GET the same id and assert Not Found (404).
    """
    payload = generate_contact_payload()
    created_id = None

    # 1) Create the contact
    create_resp = api_client.post("/contacts", token=auth_token, json=payload)
    assert_ok(create_resp)

    body = safe_json(create_resp)
    assert body is not None, "Create response body is not valid JSON"

    # extract id (supports _id, id, contactId)
    created_id = body.get("_id") or body.get("id") or body.get("contactId")
    assert created_id, f"Created contact id not found in response: {body}"

    # 2) Delete the contact — must return 200 and exact message "Contact deleted"
    del_resp = api_client.delete(f"/contacts/{created_id}", token=auth_token)

    if del_resp.status != 200:
        pretty_resp(del_resp)
        pytest.fail(f"DELETE returned unexpected status {del_resp.status}; expected 200")

    # Check exact delete message (strip to remove whitespace/newline variations)
    try:
        text = del_resp.text().strip()
    except Exception:
        text = ""
    assert text == "Contact deleted", f'Expected exact delete message "Contact deleted", got: {text!r}'

    # 3) Ensure the contact is gone: GET should return 404
    get_resp = api_client.get(f"/contacts/{created_id}", token=auth_token)
    if get_resp.status == 200:
        pretty_resp(get_resp)
        pytest.fail("Expected GET after DELETE to return not-found, but resource still exists")
    assert get_resp.status == 404, f"Expected 404 after delete, got {get_resp.status}"
