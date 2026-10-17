from pact_ai.ingestion.models import Ingested
from pact_ai.prompts.sanitize import neutralize


def tagged(tag: str, body: str) -> str:
    return f"<{tag}>\n{neutralize(body.strip())}\n</{tag}>"


def document_blocks(ingested: Ingested) -> list[str]:
    return [
        f'<documento nombre="{name}">\n{neutralize(body)}\n</documento>' for name, body in ingested.documents
    ]


def attachment_note(ingested: Ingested) -> list[str]:
    if not ingested.parts:
        return []
    return [f"Se adjuntan {len(ingested.parts)} archivo(s) (PDF o imagen) como parte de la solicitud."]
