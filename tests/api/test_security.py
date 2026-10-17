from pact_ai.core.config import get_settings


def test_health_is_open(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"


def test_token_required_when_configured(client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "secreto")
    get_settings.cache_clear()
    payload = {"text": "logo por 10 MON"}
    assert client.post("/structure-agreement", json=payload).status_code == 401
    assert client.post("/structure-agreement", json=payload, headers={"X-Internal-Token": "mal"}).status_code == 401
    ok = client.post("/structure-agreement", json=payload, headers={"X-Internal-Token": "secreto"})
    assert ok.status_code == 200
