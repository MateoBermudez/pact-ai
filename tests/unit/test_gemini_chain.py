from types import SimpleNamespace
from typing import Any

import pytest
from google.genai import errors

from pact_ai.llm import gemini
from pact_ai.schemas import ReviewDraft


class FakeClient:
    def __init__(self, *replies: Any) -> None:
        self.replies = list(replies)
        self.calls: list[dict[str, Any]] = []
        self.aio = SimpleNamespace(models=SimpleNamespace(generate_content=self._generate))

    async def _generate(self, *, model: str, contents: list, config: Any) -> Any:
        self.calls.append({"model": model, "timeout_ms": config.http_options.timeout})
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return SimpleNamespace(parsed=reply)


@pytest.fixture
def setup(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GEMINI_API_KEY", "clave")
    monkeypatch.setenv("GEMINI_MODEL", "principal")
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "respaldo")

    def install(*replies: Any) -> FakeClient:
        client = FakeClient(*replies)
        monkeypatch.setattr(gemini, "_client", lambda api_key: client)
        return client

    return install


OK = ReviewDraft(summary="ok", results=[])


async def run(timeout: float = 40) -> gemini.Generation[ReviewDraft]:
    return await gemini.generate_structured(system="s", contents=["x"], schema=ReviewDraft, timeout_seconds=timeout)


async def test_uses_the_primary_model_when_it_answers(setup) -> None:
    client = setup(OK)
    generation = await run()
    assert generation.model == "principal" and generation.parsed == OK
    assert [call["model"] for call in client.calls] == ["principal"]


async def test_falls_back_when_the_primary_fails_with_a_retryable_error(setup) -> None:
    client = setup(errors.ServerError(503, {}), OK)
    generation = await run()
    assert generation.model == "respaldo"
    assert [call["model"] for call in client.calls] == ["principal", "respaldo"]


async def test_falls_back_when_the_primary_answer_has_the_wrong_format(setup) -> None:
    setup(None, OK)
    assert (await run()).model == "respaldo"


async def test_a_non_retryable_error_does_not_try_the_fallback(setup) -> None:
    client = setup(errors.ClientError(400, {}), OK)
    with pytest.raises(gemini.GeminiError, match="400"):
        await run()
    assert len(client.calls) == 1


async def test_raises_when_every_model_fails(setup) -> None:
    client = setup(errors.ServerError(503, {}), errors.ClientError(429, {}))
    with pytest.raises(gemini.GeminiError, match="429"):
        await run()
    assert len(client.calls) == 2


async def test_every_attempt_respects_the_minimum_deadline_gemini_accepts(setup) -> None:
    client = setup(errors.ServerError(503, {}), OK)
    await run(timeout=25)
    assert all(call["timeout_ms"] >= 10_000 for call in client.calls)


async def test_does_not_call_gemini_when_there_is_no_time_left(setup) -> None:
    client = setup(OK)
    with pytest.raises(gemini.GeminiError, match="tiempo"):
        await run(timeout=5)
    assert client.calls == []


async def test_without_an_api_key_it_is_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(gemini.GeminiNotConfigured):
        await run()


def test_thinking_is_configured_with_the_form_each_model_family_accepts() -> None:
    assert gemini.thinking_config("gemini-2.5-flash").thinking_budget == 0
    for model in ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"):
        config = gemini.thinking_config(model)
        assert config.thinking_level is not None and config.thinking_budget is None
    assert gemini.thinking_config("gemini-3.1-pro-preview") is None
