from typing import TypeVar

from google.genai import types
from pydantic import BaseModel

from pact_ai.core.errors import AiNotConfigured, AiUpstreamError
from pact_ai.llm import gemini

T = TypeVar("T", bound=BaseModel)


async def generate(
    schema: type[T], system: str, contents: list[types.Part | str], timeout_seconds: float
) -> gemini.Generation[T]:
    try:
        return await gemini.generate_structured(
            system=system, contents=contents, schema=schema, timeout_seconds=timeout_seconds
        )
    except gemini.GeminiNotConfigured as error:
        raise AiNotConfigured("La IA no está configurada") from error
    except gemini.GeminiError as error:
        raise AiUpstreamError(str(error)) from error
