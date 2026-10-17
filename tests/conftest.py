import base64
import io
from collections.abc import Callable
from typing import Any

import pytest
from docx import Document
from fastapi.testclient import TestClient

from pact_ai.llm import gemini
from pact_ai.main import app


class FakeGemini:
    def __init__(self, model: str = "fake-model") -> None:
        self.model = model
        self.reply: Callable[[type], Any] = lambda schema: (_ for _ in ()).throw(AssertionError("sin respuesta"))
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, *, system: str, contents: list, schema: type, timeout_seconds: float) -> Any:
        self.calls.append({"system": system, "contents": contents, "schema": schema, "timeout": timeout_seconds})
        result = self.reply(schema)
        if isinstance(result, Exception):
            raise result
        return gemini.Generation(parsed=result, model=self.model)


@pytest.fixture
def fake(monkeypatch: pytest.MonkeyPatch) -> FakeGemini:
    fake_gemini = FakeGemini()
    monkeypatch.setattr(gemini, "generate_structured", fake_gemini)
    monkeypatch.delenv("PACT_AI_SHARED_SECRET", raising=False)
    return fake_gemini


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def make_docx(*paragraphs: str) -> bytes:
    buffer = io.BytesIO()
    document = Document()
    for paragraph in paragraphs:
        document.add_paragraph(paragraph)
    document.save(buffer)
    return buffer.getvalue()
