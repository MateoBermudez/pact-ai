from typing import Any

from pact_ai.ingestion.models import Ingested
from pact_ai.prompts.blocks import attachment_note, document_blocks, tagged
from pact_ai.prompts.loader import load_system_prompt

REVIEW_SYSTEM = load_system_prompt("review")


def build_review_contents(
    requirements: str,
    provider_note: str,
    evidence_url: str,
    ingested: Ingested,
) -> list[Any]:
    blocks = [
        tagged("requisitos", requirements),
        tagged("nota_proveedor", provider_note.strip() or "(sin nota)"),
        tagged("enlace_evidencia", evidence_url.strip() or "(sin enlace)"),
    ]
    blocks.extend(document_blocks(ingested))
    blocks.extend(attachment_note(ingested))
    return ["\n\n".join(blocks), *ingested.parts]
