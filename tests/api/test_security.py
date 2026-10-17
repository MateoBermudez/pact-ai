from fastapi.testclient import TestClient

from pact_ai.schemas import RuleDraft, StructureDraft
from tests.conftest import FakeGemini

BODY = {"text": "Quiero un logo"}


def a_draft() -> StructureDraft:
    return StructureDraft(
        title="t",
        description="d",
        amount_mon=None,
        days=None,
        category=None,
        keywords=[],
        rules=[RuleDraft(criterion="Regla de prueba", weight=3)],
    )


def test_with_a_shared_secret_only_the_caller_that_knows_it_gets_in(
    client: TestClient, fake: FakeGemini, monkeypatch
) -> None:
    fake.reply = lambda schema: a_draft()
    monkeypatch.setenv("PACT_AI_SHARED_SECRET", "secreto-largo")

    assert client.post("/structure-agreement", json=BODY).status_code == 401
    assert client.post("/structure-agreement", json=BODY, headers={"x-pact-ai-secret": "otro"}).status_code == 401
    assert (
        client.post("/structure-agreement", json=BODY, headers={"x-pact-ai-secret": "secreto-largo"}).status_code == 200
    )
    assert client.post("/review-evidence", json={}, headers={"x-pact-ai-secret": "otro"}).status_code == 401
    assert fake.calls and len(fake.calls) == 1


def test_health_stays_open(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("PACT_AI_SHARED_SECRET", "secreto-largo")
    assert client.get("/health").json() == {"status": "ok"}


def test_without_a_configured_secret_the_service_is_open_for_local_development(
    client: TestClient, fake: FakeGemini
) -> None:
    fake.reply = lambda schema: a_draft()
    assert client.post("/structure-agreement", json=BODY).status_code == 200
