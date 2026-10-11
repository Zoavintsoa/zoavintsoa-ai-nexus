"""Small retrying JSON HTTP helper; uses only the Python standard library."""
from __future__ import annotations

import json
import logging
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from nexus.errors import ProviderError

_LOG = logging.getLogger("nexus.http")
_RETRYABLE_STATUS = {408, 425, 429}


def request_json(host: str, path: str, timeout: float, payload: dict | None = None,
                 api_key: str | None = None, attempts: int = 3) -> dict:
    """Request JSON with bounded retries for transient network/server failures."""
    request_id = uuid.uuid4().hex[:12]
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json", "X-Request-ID": request_id}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    attempts = max(1, min(int(attempts), 4))

    for attempt in range(attempts):
        request = Request(host.rstrip("/") + path, data=data, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
            if not isinstance(result, dict):
                raise ProviderError(f"API at {host} returned an unexpected response (request {request_id}).")
            return result
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            retryable = exc.code in _RETRYABLE_STATUS or exc.code >= 500
            if not retryable or attempt + 1 >= attempts:
                raise ProviderError(
                    f"API at {host} returned HTTP {exc.code}: {detail} (request {request_id})."
                ) from exc
            _LOG.warning("Transient HTTP error request_id=%s status=%s attempt=%s/%s",
                         request_id, exc.code, attempt + 1, attempts)
        except (URLError, TimeoutError, OSError) as exc:
            if attempt + 1 >= attempts:
                raise ProviderError(
                    f"Cannot reach API at {host}. Check that the server is running "
                    f"({exc}; request {request_id})."
                ) from exc
            _LOG.warning("Transient transport error request_id=%s attempt=%s/%s error=%s",
                         request_id, attempt + 1, attempts, type(exc).__name__)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError(f"API at {host} returned invalid JSON (request {request_id}).") from exc
        time.sleep(min(0.25 * (2 ** attempt), 1.0))

    raise ProviderError(f"Request failed unexpectedly (request {request_id}).")
