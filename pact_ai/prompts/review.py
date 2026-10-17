from pact_ai.prompts.loader import load_system_prompt
from pact_ai.prompts.sanitize import neutralize
from pact_ai.schemas import ReviewEvidenceIn

REVIEW_SYSTEM = load_system_prompt("review")


def review_prompt(data: ReviewEvidenceIn) -> str:
    rules = "\n".join(f"{rule.position}. (peso {rule.weight}) {neutralize(rule.criterion)}" for rule in data.rules)
    return (
        f"<requisitos>\n{neutralize(data.requirements)}\n</requisitos>\n\n"
        f"<reglas>\n{rules}\n</reglas>\n\n"
        f"<entrega>\nNota del proveedor: {neutralize(data.provider_note) or '(sin nota)'}\n"
        f"Enlace: {neutralize(data.evidence_url)}\n</entrega>"
    )
