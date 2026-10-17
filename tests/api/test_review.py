from pact_ai.schemas import ChecklistItem
from tests.helpers import PNG_BYTES

PAYLOAD = {
    "requirements": "Logo en PNG y SVG",
    "provider_note": "Entregué ambos formatos",
    "evidence_url": "https://drive.google.com/file/d/abc",
}


def met(value: bool) -> ChecklistItem:
    return ChecklistItem(criterion="PNG", met=value, comment="")


def test_review_cumple(client, llm):
    llm.review = llm.review.model_copy(update={"checklist": [met(True)]})
    body = client.post("/review-evidence", json=PAYLOAD).json()
    assert body["verdict"] == "cumple"
    assert body["meta"]["input_tokens"] == 10


def test_unmet_item_forces_revisar(client, llm):
    llm.review = llm.review.model_copy(update={"verdict": "cumple", "checklist": [met(True), met(False)]})
    assert client.post("/review-evidence", json=PAYLOAD).json()["verdict"] == "revisar"


def test_empty_checklist_never_cumple(client, llm):
    assert client.post("/review-evidence", json=PAYLOAD).json()["verdict"] == "revisar"


def test_confidence_is_clamped(client, llm):
    llm.review = llm.review.model_copy(update={"checklist": [met(True)], "confidence": 7})
    assert client.post("/review-evidence", json=PAYLOAD).json()["confidence"] == 1.0


def test_llm_down_defaults_to_revisar(client, llm):
    llm.fail = True
    body = client.post("/review-evidence", json=PAYLOAD).json()
    assert body["verdict"] == "revisar"
    assert body["meta"]["source"] == "fallback"


def test_requirements_required(client):
    assert client.post("/review-evidence", json={**PAYLOAD, "requirements": ""}).status_code == 422


def test_review_with_image_evidence(client, llm):
    res = client.post(
        "/review-evidence/files",
        data=PAYLOAD,
        files=[("files", ("logo.png", PNG_BYTES, "image/png"))],
    )
    assert res.status_code == 200
    assert len(llm.calls[-1]["contents"]) == 2
