import logging
import time
from typing import Any

import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from pact_ai.core.config import Settings
from pact_ai.core.errors import LLMUnavailable
from pact_ai.llm.base import T
from pact_ai.schemas.common import Meta

logger = logging.getLogger("pact_ai.llm")

RETRYABLE_CODES = {408, 429, 500, 502, 503, 504}
MIN_ATTEMPT_SECONDS = 10.0


class GeminiLLM:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None
        models = [settings.gemini_model]
        if settings.gemini_fallback_model and settings.gemini_fallback_model != settings.gemini_model:
            models.append(settings.gemini_fallback_model)
        self._models = models

    def generate(self, system: str, contents: list[Any], schema: type[T]) -> tuple[T, Meta]:
        if self._client is None:
            raise LLMUnavailable("GEMINI_API_KEY no configurada")

        deadline = time.monotonic() + self._settings.llm_total_budget
        last_error: Exception | None = None

        for model in self._models:
            remaining = deadline - time.monotonic()
            if remaining < MIN_ATTEMPT_SECONDS:
                break
            timeout = min(self._settings.llm_attempt_timeout, remaining)
            started = time.monotonic()
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        temperature=self._settings.temperature,
                        response_mime_type="application/json",
                        response_schema=schema,
                        http_options=types.HttpOptions(timeout=int(timeout * 1000)),
                    ),
                )
                parsed = schema.model_validate_json(response.text or "")
            except errors.APIError as exc:
                last_error = exc
                logger.warning("gemini %s falló: %s %s", model, exc.code, exc.status)
                if exc.code not in RETRYABLE_CODES:
                    break
                continue
            except (ValidationError, ValueError, httpx.HTTPError, OSError) as exc:
                last_error = exc
                logger.warning("gemini %s falló: %s: %s", model, type(exc).__name__, str(exc)[:300])
                continue

            usage = response.usage_metadata
            meta = Meta(
                model=model,
                source="gemini",
                input_tokens=(usage.prompt_token_count or 0) if usage else 0,
                output_tokens=(usage.candidates_token_count or 0) if usage else 0,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            return parsed, meta

        raise LLMUnavailable(str(last_error) if last_error else "sin presupuesto de tiempo")
