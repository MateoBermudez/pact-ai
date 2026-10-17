from pact_ai.core.config import Settings
from pact_ai.fallback.rules import MISSING_AMOUNT_QUESTION, MISSING_DAYS_QUESTION
from pact_ai.schemas import AgreementExtraction, Meta, StructureAgreementOut

DESCRIPTION_MAX_BYTES = 500
MAX_DAYS = 365
AMOUNT_DECIMALS = 4
TITLE_MAX_CHARS = 80
MISSING_DESCRIPTION_QUESTION = "¿Qué trabajo quieres contratar?"


def fit_bytes(text: str, limit: int) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed.encode()) <= limit:
        return collapsed
    budget = limit - len("…".encode())
    clipped = collapsed.encode()[:budget].decode(errors="ignore")
    head, _, tail = clipped.rpartition(" ")
    return (head if head and len(tail) < 20 else clipped).rstrip(" ,;:.") + "…"


def normalize_amount(amount: float | None, settings: Settings, warnings: list[str]) -> float | None:
    if not amount:
        return None
    rounded = round(amount, AMOUNT_DECIMALS)
    if rounded > settings.max_amount_mon:
        warnings.append(f"El monto supera el máximo permitido ({settings.max_amount_mon:g} MON).")
        return None
    return rounded


def normalize_days(days: int | None) -> int | None:
    if days and 1 <= days <= MAX_DAYS:
        return days
    return None


def build_structure_output(
    extraction: AgreementExtraction, meta: Meta, settings: Settings
) -> StructureAgreementOut:
    warnings = list(extraction.warnings)
    questions = list(extraction.questions)

    amount = normalize_amount(extraction.amount_mon, settings, warnings)
    days = normalize_days(extraction.days)
    description = fit_bytes(extraction.description, DESCRIPTION_MAX_BYTES)

    missing: list[str] = []
    if amount is None:
        missing.append(MISSING_AMOUNT_QUESTION)
    if days is None:
        missing.append(MISSING_DAYS_QUESTION)
    if not description:
        missing.append(MISSING_DESCRIPTION_QUESTION)

    return StructureAgreementOut(
        status="needs_clarification" if missing else "ok",
        description=description,
        amount_mon=amount,
        days=days,
        title=extraction.title.strip()[:TITLE_MAX_CHARS],
        deliverables=extraction.deliverables,
        acceptance_criteria=extraction.acceptance_criteria,
        category=extraction.category,
        skills=extraction.skills,
        suggested_milestones=extraction.suggested_milestones,
        warnings=warnings,
        questions=questions or missing,
        meta=meta,
    )
