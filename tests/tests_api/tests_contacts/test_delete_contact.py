import pytest
from tests.utils import pretty_resp


@pytest.mark.usefixtures("auth_token")
def test_delete_contact(api_client, contact_resource, auth_token):
    """
    Delete contact test that uses contact_resource fixture. We expect the fixture to have created the contact.
    This test deletes the contact explicitly (so the fixture teardown has no-op delete) and asserts the expected 200 + exact message.
    """
    cid = contact_resource["id"]

    # Delete
    del_resp = api_client.delete(f"/contacts/{cid}", token=auth_token)
    if del_resp.status != 200:
        pretty_resp(del_resp)
        pytest.fail(f"Expected DELETE 200, got {del_resp.status}")

    try:
        text = del_resp.text().strip()
    except Exception:
        text = ""
    assert text == "Contact deleted", f"Unexpected delete text: {text!r}"

    # Confirm not found
    get_after = api_client.get(f"/contacts/{cid}", token=auth_token)
    assert get_after.status in (404, 400)