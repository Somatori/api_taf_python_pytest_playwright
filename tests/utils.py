import json
from typing import Any, Dict, Optional
from playwright.sync_api import Response


def safe_json(resp: Response) -> Optional[Any]:
    """
    Try to parse the response body as JSON. On failure return None.
    Use this to avoid exceptions when the API returns HTML or empty bodies on error.
    """
    try:
        return resp.json()
    except Exception:
        return None


def text_or_json(resp: Response) -> str:
    """
    Return a pretty-printed JSON string when possible, otherwise return the plain text body.
    Truncates large output to keep logs readable.
    """
    MAX = 8000
    body = safe_json(resp)
    if body is not None:
        try:
            s = json.dumps(body, indent=2, ensure_ascii=False)
        except Exception:
            s = str(body)
    else:
        try:
            s = resp.text()
        except Exception:
            s = "<unable to read body>"

    if len(s) > MAX:
        return s[:MAX] + "\n...(truncated)"
    return s


def pretty_resp(resp: Response, show_headers: bool = True) -> None:
    """
    Print a concise, helpful dump of a Playwright Response for debugging.
    Example output:
      STATUS: 200
      HEADERS: {...}
      BODY:
      {
        ...
      }
    """
    print(f"\n--- HTTP {resp.status} {resp.url} ---")
    if show_headers:
        try:
            hdrs = dict(resp.headers)
            print("HEADERS:", json.dumps(hdrs, indent=2, ensure_ascii=False))
        except Exception:
            print("HEADERS: <unable to read headers>")
    print("BODY:")
    print(text_or_json(resp))
    print("--- end response ---\n")


def assert_status(resp: Response, expected: int) -> None:
    """
    Assert the response status is the expected value. On failure show a helpful dump.
    """
    if resp.status != expected:
        # Print helpful details and raise AssertionError
        pretty_resp(resp)
        raise AssertionError(f"Expected status {expected}, got {resp.status}")


def assert_ok(resp: Response) -> None:
    """
    Assert the response is a 2xx. On failure print helpful details.
    """
    if not (200 <= resp.status < 300):
        pretty_resp(resp)
        raise AssertionError(f"Expected 2xx response, got {resp.status}")
