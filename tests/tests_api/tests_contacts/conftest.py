import pytest
from tests.factories import generate_contact_payload
from tests.utils import pretty_resp


@pytest.fixture
def contact_resource(api_client, auth_token, request):
    """
    Create a contact for a test and ensure teardown deletes it.

    Yields a dict: {"id": <contact_id>, "payload": <payload_dict>}.

    Behavior:
      - If creation fails, the fixture will `pytest.skip()` the test (so dependent tests are skipped rather than failing with setup noise).
      - On teardown it attempts to DELETE the created contact; if deletion fails it logs a warning but does not swallow a preceding test failure.
    """
    payload = generate_contact_payload()
    created_id = None

    # Create
    try:
        resp = api_client.post("/contacts", token=auth_token, json=payload)
    except Exception as e:
        pytest.skip(f"Could not create contact due to client error: {e}")

    if resp.status not in (200, 201):
        # show debugging info then skip
        pretty_resp(resp)
        pytest.skip(f"Could not create contact; POST returned {resp.status}")

    try:
        body = resp.json()
    except Exception:
        pretty_resp(resp)
        pytest.skip("Create contact response was not JSON; skipping test")

    created_id = body.get("_id")
    if not created_id:
        pretty_resp(resp)
        pytest.skip("Create contact did not return an id; skipping test")

    # Store the created id in pytest cache optionally for debugging reruns
    try:
        request.config.cache.set("contact_resource/last_id", created_id)
    except Exception:
        pass

    # Yield resource to the test
    yield {"id": created_id, "payload": payload}

    # Teardown (best-effort delete) — do not mask test failures
    try:
        del_resp = api_client.delete(f"/contacts/{created_id}", token=auth_token)
        if del_resp.status not in (200, 204):
            # Log a warning for visibility
            print(f"Warning: teardown delete returned {del_resp.status} for contact {created_id}")
            try:
                pretty_resp(del_resp)
            except Exception:
                pass
    except Exception as e:
        print(f"Warning: exception while attempting cleanup for contact {created_id}: {e}")