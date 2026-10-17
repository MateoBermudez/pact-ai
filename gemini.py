import os
from functools import lru_cache
from typing import TypeVar

from google import genai
from google.genai import errors, types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiNotConfigured(Exception):
    pass


class GeminiError(Exception):
    pass


def model_name() -> str:
    return os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiNotConfigured("Falta GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


async def generate_structured(
    *,
    system: str,
    contents: list[types.Part | str],
    schema: type[T],
    timeout_seconds: float,
) -> T:
    """Pide a Gemini una respuesta JSON con la forma de `schema` y la devuelve ya parseada."""
    model = model_name()
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        response_schema=schema,
        temperature=0.2,
        http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
        # La extracción estructurada no necesita razonamiento largo: apagarlo baja latencia y costo en los modelos flash.
        thinking_config=types.ThinkingConfig(thinking_budget=0) if "flash" in model else None,
    )
    try:
        response = await _client().aio.models.generate_content(model=model, contents=contents, config=config)
    except errors.APIError as error:
        raise GeminiError(f"Gemini respondió {error.code}") from error
    except Exception as error:
        raise GeminiError(f"No se pudo consultar a Gemini: {type(error).__name__}") from error

    parsed = response.parsed
    if not isinstance(parsed, schema):
        raise GeminiError("Gemini devolvió una respuesta vacía o con formato inválido")
    return parsed
