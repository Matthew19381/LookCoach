"""Module-to-module authentication (X-Module-Key) shared by the integration routers.

- `require_module_key`: the header must match env MODULE_KEY (401 otherwise).
- `require_module_key_or_local`: same when the header is sent; without it the
  request is accepted only from this machine. Used for POST /directives because
  the hub's broadcast_directive did not send the key (plan 2.3 / H-4); once the
  hub sends it, a wrong key is rejected even from localhost.

Comparison uses hmac.compare_digest (constant time).
"""
import hmac
import os

from fastapi import Header, HTTPException, Request

# "testclient" is Starlette's TestClient; a real socket peer is always an IP.
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


def _key_matches(given: str | None) -> bool:
    expected = os.getenv("MODULE_KEY")
    if not expected or not given:
        return False
    return hmac.compare_digest(given.encode(), expected.encode())


def require_module_key(x_module_key: str | None = Header(None)) -> None:
    if not _key_matches(x_module_key):
        raise HTTPException(status_code=401, detail="Invalid X-Module-Key")


def require_module_key_or_local(request: Request, x_module_key: str | None = Header(None)) -> None:
    if x_module_key is not None:
        if not _key_matches(x_module_key):
            raise HTTPException(status_code=401, detail="Invalid X-Module-Key")
        return
    host = request.client.host if request.client else None
    if host not in LOCAL_HOSTS:
        raise HTTPException(status_code=401, detail="X-Module-Key required outside localhost")
