import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Generic, TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from pact_ai.core.config import get_settings

T = TypeVar("T", bound=BaseModel)

MIN_ATTEMPT_SECONDS = 10.0
RETRYABLE_CODES = {408, 429, 500, 502, 503, 504}


class GeminiNotConfigured(Exception):
    pass


class GeminiError(Exception):
    pass


@dataclass(frozen=True)
class Generation(Generic[T]):
    parsed: T
    model: str


@lru_cache(maxsize=2)
def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def thinking_config(model: str) -> types.ThinkingConfig | None:
    if "flash" not in model:
        return None
    if model.startswith("gemini-2.5"):
        return types.ThinkingConfig(thinking_budget=0)
    return types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL)


def _config(system: str, schema: type[BaseModel], model: str, timeout_seconds: float) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        response_schema=schema,
        temperature=0.2,
        http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
        thinking_config=thinking_config(model),
    )


async def generate_structured(
    *,
    system: str,
    contents: list[types.Part | str],
    schema: type[T],
    timeout_seconds: float,
) -> Generation[T]:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise GeminiNotConfigured("Falta GEMINI_API_KEY")

    client = _client(settings.gemini_api_key)
    deadline = time.monotonic() + timeout_seconds
    models = settings.gemini_models
    last_error: GeminiError | None = None

    for index, model in enumerate(models):
        remaining = deadline - time.monotonic()
        if remaining < MIN_ATTEMPT_SECONDS:
            break
        is_last = index == len(models) - 1
        attempt_timeout = remaining if is_last else max(MIN_ATTEMPT_SECONDS, remaining - MIN_ATTEMPT_SECONDS)

        try:
            response = await client.aio.models.generate_content(
                model=model, contents=contents, config=_config(system, schema, model, attempt_timeout)
            )
        except errors.APIError as error:
            last_error = GeminiError(f"Gemini respondió {error.code}")
            if error.code not in RETRYABLE_CODES:
                break
            continue
        except (httpx.HTTPError, OSError, ValueError) as error:
            last_error = GeminiError(f"No se pudo consultar a Gemini: {type(error).__name__}")
            continue

        parsed = response.parsed
        if not isinstance(parsed, schema):
            last_error = GeminiError("Gemini devolvió una respuesta vacía o con formato inválido")
            continue
        return Generation(parsed=parsed, model=model)

    raise last_error or GeminiError("No quedó tiempo para consultar a Gemini")
