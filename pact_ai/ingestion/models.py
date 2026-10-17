from dataclasses import dataclass, field

from google.genai import types


@dataclass
class Ingested:
    parts: list[types.Part] = field(default_factory=list)
    documents: list[tuple[str, str]] = field(default_factory=list)
    fingerprint: list[bytes] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.parts) + len(self.documents)
