import base64
from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient

import gemini
import main


class FakeGemini:
    """Sustituye la llamada real a Gemini: devuelve lo que el test decida y guarda lo que recibió."""

    def __init__(self) -> None:
        self.reply: Callable[[type], Any] = lambda schema: (_ for _ in ()).throw(AssertionError("sin respuesta"))
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, *, system: str, contents: list, schema: type, timeout_seconds: float) -> Any:
        self.calls.append({"system": system, "contents": contents, "schema": schema, "timeout": timeout_seconds})
        result = self.reply(schema)
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture
def fake(monkeypatch: pytest.MonkeyPatch) -> FakeGemini:
    fake_gemini = FakeGemini()
    monkeypatch.setattr(gemini, "generate_structured", fake_gemini)
    monkeypatch.delenv("PACT_AI_SHARED_SECRET", raising=False)
    return fake_gemini


@pytest.fixture
def client() -> TestClient:
    return TestClient(main.app)


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()
