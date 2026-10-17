from typing import TypeVar

from pact_ai.schemas import ReviewEvidenceOut, StructureAgreementOut

R = TypeVar("R", StructureAgreementOut, ReviewEvidenceOut)


def mark_cached(result: R) -> R:
    return result.model_copy(update={"meta": result.meta.model_copy(update={"source": "cache"})})
