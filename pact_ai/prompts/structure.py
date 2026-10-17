import json

from pact_ai.prompts.loader import load_system_prompt
from pact_ai.prompts.sanitize import neutralize
from pact_ai.schemas import CATEGORIES, PreviousAgreement

STRUCTURE_SYSTEM = load_system_prompt("structure", categories=", ".join(CATEGORIES))


def structure_prompt(text: str | None) -> str:
    return f"<solicitud>\n{neutralize(text.strip())}\n</solicitud>" if text and text.strip() else ""


def structure_file_label(file_name: str) -> str:
    return f"<archivo nombre={neutralize(file_name)!r}>"


def refinement_prompt(previous: PreviousAgreement | None, feedback: str | None) -> list[str]:
    if previous is None or not feedback or not feedback.strip():
        return []
    current = neutralize(json.dumps(previous.model_dump(), ensure_ascii=False))
    return [
        f"<borrador_actual>\n{current}\n</borrador_actual>",
        f"<cambio_solicitado>\n{neutralize(feedback.strip())}\n</cambio_solicitado>",
    ]
