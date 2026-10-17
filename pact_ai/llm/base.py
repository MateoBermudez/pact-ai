from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from pact_ai.schemas.common import Meta

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    def generate(self, system: str, contents: list[Any], schema: type[T]) -> tuple[T, Meta]: ...
