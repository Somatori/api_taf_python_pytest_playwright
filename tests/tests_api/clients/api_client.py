class ApiClient:
    """
    Minimal wrapper around Playwright's APIRequestContext to centralize common behavior.
    Usage:
        client = ApiClient(api_request_context)
        resp = client.post("/contacts", token=token, json=payload)
    """
    def __init__(self, request_context):
        self._ctx = request_context

    def _auth_headers(self, token):
        return {"Authorization": f"Bearer {token}"} if token else {}

    def get(self, path, token=None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))
        return self._ctx.get(path, headers=headers, **kwargs)

    def post(self, path, token=None, json=None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))
        return self._ctx.post(path, json=json, headers=headers, **kwargs)

    def put(self, path, token=None, json=None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))
        return self._ctx.put(path, json=json, headers=headers, **kwargs)

    def patch(self, path, token=None, json=None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))
        return self._ctx.patch(path, json=json, headers=headers, **kwargs)

    def delete(self, path, token=None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))
        return self._ctx.delete(path, headers=headers, **kwargs)
