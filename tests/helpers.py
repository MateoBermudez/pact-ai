import io
from typing import Any

from docx import Document

from pact_ai.core.errors import LLMUnavailable
from pact_ai.schemas import AgreementExtraction, Meta, ReviewExtraction

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
PDF_BYTES = b"%PDF-1.4\n" + b"0" * 32


def make_docx(text: str) -> bytes:
    buffer = io.BytesIO()
    document = Document()
    document.add_paragraph(text)
    document.save(buffer)
    return buffer.getvalue()


class FakeLLM:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.structure = AgreementExtraction(
            description="Logo para una cafetería",
            amount_mon=10,
            days=5,
            title="Logo cafetería",
            deliverables=["PNG", "SVG"],
            acceptance_criteria=["Entrega en PNG y SVG"],
            category="diseño",
            skills=["diseño gráfico"],
            suggested_milestones=[],
            warnings=[],
            questions=[],
        )
        self.review = ReviewExtraction(
            verdict="cumple",
            reason="La nota cubre los requisitos.",
            checklist=[],
            confidence=0.9,
        )
        self.fail = False

    def generate(self, system: str, contents: list[Any], schema: type) -> tuple[Any, Meta]:
        self.calls.append({"system": system, "contents": contents, "schema": schema})
        if self.fail:
            raise LLMUnavailable("caído")
        meta = Meta(model="fake", source="gemini", input_tokens=10, output_tokens=5, latency_ms=1)
        if schema is AgreementExtraction:
            return self.structure, meta
        return self.review, meta
