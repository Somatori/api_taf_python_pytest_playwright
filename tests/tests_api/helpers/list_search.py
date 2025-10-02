"""
Helpers to search the /contacts list safely (bounded pagination).
"""

from typing import Optional, Dict, Any


def find_in_contacts_list(
    api_client,
    auth_token: str,
    created_id: Optional[str] = None,
    email: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    page_param: str = "page",
    limit_param: str = "limit",
    page_size: int = 100,
    max_pages: int = 10,
) -> Optional[Dict[str, Any]]:
    """
    Try to find a contact in GET /contacts using safe pagination.

    - api_client: your ApiClient instance fixture
    - auth_token: bearer token string
    - created_id: if provided, match by _id / id / contactId
    - email: if provided, match by email
    - params: extra query params to send (will be updated with page/limit)
    - page_param / limit_param: query param names used by the API for paging
    - page_size: number of items per page to request
    - max_pages: maximum pages to check (to avoid scanning thousands of items)

    Returns the matching contact dict if found, otherwise None.
    """
    params = dict(params or {})

    for page in range(1, max_pages + 1):
        # Update paging params for this iteration
        params.update({limit_param: page_size, page_param: page})

        resp = api_client.get("/contacts", token=auth_token, params=params)
        if resp is None:
            return None

        # stop searching on server error
        if resp.status != 200:
            return None

        try:
            items = resp.json()
        except Exception:
            # Response was not JSON: nothing to do
            return None

        if not isinstance(items, list):
            return None

        # scan this page
        for item in items:
            if created_id and (
                item.get("_id") == created_id
                or item.get("id") == created_id
                or item.get("contactId") == created_id
            ):
                return item
            if email and item.get("email") == email:
                return item

        # If this page returned fewer items than requested, assume last page => stop early
        if len(items) < page_size:
            break

    return None
