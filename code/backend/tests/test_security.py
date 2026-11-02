"""Plan 2.3: X-Module-Key checks (constant time) and the localhost rule for /directives."""
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend import security


def _app():
    app = FastAPI()

    @app.post("/strict", dependencies=[Depends(security.require_module_key)])
    def strict():
        return {"ok": True}

    @app.post("/local", dependencies=[Depends(security.require_module_key_or_local)])
    def local():
        return {"ok": True}

    return app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("MODULE_KEY", "secret-key")
    return TestClient(_app())


def test_strict_requires_correct_key(client):
    assert client.post("/strict").status_code == 401
    assert client.post("/strict", headers={"X-Module-Key": "nope"}).status_code == 401
    assert client.post("/strict", headers={"X-Module-Key": "secret-key"}).status_code == 200


def test_strict_rejects_everything_when_no_key_configured(monkeypatch):
    monkeypatch.setenv("MODULE_KEY", "")
    c = TestClient(_app())
    assert c.post("/strict", headers={"X-Module-Key": ""}).status_code == 401


def test_local_without_header_is_allowed_from_this_machine(client):
    assert client.post("/local").status_code == 200


def test_wrong_key_is_rejected_even_locally(client):
    assert client.post("/local", headers={"X-Module-Key": "nope"}).status_code == 401


def test_no_header_from_lan_is_rejected(monkeypatch):
    monkeypatch.setattr(security, "LOCAL_HOSTS", {"127.0.0.1"})  # TestClient host is not local now
    c = TestClient(_app())
    assert c.post("/local").status_code == 401
    monkeypatch.setenv("MODULE_KEY", "secret-key")
    assert c.post("/local", headers={"X-Module-Key": "secret-key"}).status_code == 200
