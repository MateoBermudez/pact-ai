from pact_ai.fallback.parsing import parse_amount, parse_days
from pact_ai.schemas import Meta, ReviewEvidenceOut, StructureAgreementOut

MISSING_AMOUNT_QUESTION = "¿Cuántos MON quieres depositar en el acuerdo?"
MISSING_DAYS_QUESTION = "¿En cuántos días necesitas la entrega?"


def fallback_meta() -> Meta:
    return Meta(model="rules", source="fallback")


def structure_from_rules(text: str) -> StructureAgreementOut:
    cleaned = " ".join(text.split())
    amount = parse_amount(cleaned)
    days = parse_days(cleaned)
    questions: list[str] = []
    if amount is None:
        questions.append(MISSING_AMOUNT_QUESTION)
    if days is None:
        questions.append(MISSING_DAYS_QUESTION)
    return StructureAgreementOut(
        status="ok" if not questions else "needs_clarification",
        description=cleaned,
        amount_mon=amount,
        days=days,
        warnings=["Borrador generado sin IA; revisa los datos antes de firmar."],
        questions=questions,
        meta=fallback_meta(),
    )


def review_from_rules() -> ReviewEvidenceOut:
    return ReviewEvidenceOut(
        verdict="revisar",
        reason="No se pudo analizar la entrega automáticamente; revísala manualmente antes de aprobar.",
        meta=fallback_meta(),
    )
