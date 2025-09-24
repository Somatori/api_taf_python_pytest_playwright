import json as _json
from typing import Any, Dict, Optional


class ApiClient:
    """
    Wrapper around Playwright's APIRequestContext.
    Accepts `json=` in methods (like requests) and converts it to a JSON body
    suitable for Playwright's request methods that expect `data=` / raw body.
    """

    def __init__(self, request_context):
        self._ctx = request_context

    def _auth_headers(self, token: Optional[str]) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _prepare_headers_for_json(self, headers: Dict[str, str]) -> Dict[str, str]:
        # ensure we don't overwrite a pre-existing Content-Type
        headers = dict(headers or {})
        headers.setdefault("Content-Type", "application/json")
        return headers

    def get(self, path: str, token: Optional[str] = None, params: Dict[str, Any] = None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))
        return self._ctx.get(path, params=params, headers=headers, **kwargs)

    def post(self, path: str, token: Optional[str] = None, json: Any = None, data: Any = None, **kwargs):
        """
        If `json` is provided, it will be serialized and sent as the request body
        with Content-Type: application/json. Otherwise `data` is forwarded as-is.
        """
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))

        if json is not None:
            headers = self._prepare_headers_for_json(headers)
            body = _json.dumps(json)
            return self._ctx.post(path, data=body, headers=headers, **kwargs)
        else:
            return self._ctx.post(path, data=data, headers=headers, **kwargs)

    def put(self, path: str, token: Optional[str] = None, json: Any = None, data: Any = None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))

        if json is not None:
            headers = self._prepare_headers_for_json(headers)
            body = _json.dumps(json)
            return self._ctx.put(path, data=body, headers=headers, **kwargs)
        else:
            return self._ctx.put(path, data=data, headers=headers, **kwargs)

    def patch(self, path: str, token: Optional[str] = None, json: Any = None, data: Any = None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))

        if json is not None:
            headers = self._prepare_headers_for_json(headers)
            body = _json.dumps(json)
            return self._ctx.patch(path, data=body, headers=headers, **kwargs)
        else:
            return self._ctx.patch(path, data=data, headers=headers, **kwargs)

    def delete(self, path: str, token: Optional[str] = None, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers(token))
        return self._ctx.delete(path, headers=headers, **kwargs)

    # ---- Helper methods for user auth ----
    def register_user(self, token: str, email: str, password: str):
        """
        Register a new user. Requires token because API needs auth for creation.
        Returns the Playwright Response object.
        """
        if not token:
            raise ValueError("register_user requires an authorization token (pass token=<str>).")
        return self.post("/users", token=token, json={"email": email, "password": password})

    def login_user(self, email: str, password: str) -> Optional[str]:
        """
        Login and return the token string (if present) or None.
        """
        resp = self.post("/users/login", json={"email": email, "password": password})
        try:
            body = resp.json()
        except Exception:
            body = {}

        for key in ("token", "accessToken", "access_token", "auth_token"):
            if key in body:
                return body[key]

        if isinstance(body.get("user"), dict):
            for key in ("token", "accessToken", "access_token", "auth_token"):
                if key in body["user"]:
                    return body["user"][key]

        return None
