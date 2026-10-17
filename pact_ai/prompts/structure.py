from typing import Any

from pact_ai.ingestion.models import Ingested
from pact_ai.prompts.blocks import attachment_note, document_blocks, tagged
from pact_ai.prompts.loader import load_system_prompt
from pact_ai.schemas.agreement import AgreementDraft

STRUCTURE_SYSTEM = load_system_prompt("structure")


def build_structure_contents(
    text: str | None,
    previous: AgreementDraft | None,
    feedback: str | None,
    ingested: Ingested,
) -> list[Any]:
    blocks: list[str] = []
    if text and text.strip():
        blocks.append(tagged("solicitud", text))
    blocks.extend(document_blocks(ingested))
    if previous is not None and feedback and feedback.strip():
        blocks.append(f"<borrador_actual>\n{previous.model_dump_json()}\n</borrador_actual>")
        blocks.append(tagged("cambio_solicitado", feedback))
    blocks.extend(attachment_note(ingested))
    return ["\n\n".join(blocks), *ingested.parts]
