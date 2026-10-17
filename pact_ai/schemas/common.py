from typing import Literal

from pydantic import BaseModel


class Meta(BaseModel):
    model: str
    source: Literal["gemini", "fallback", "cache"]
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
