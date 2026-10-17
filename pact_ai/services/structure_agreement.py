from pact_ai.core.cache import TTLCache, make_key
from pact_ai.core.config import Settings
from pact_ai.core.errors import LLMUnavailable
from pact_ai.fallback import structure_from_rules
from pact_ai.ingestion import Ingested
from pact_ai.llm.base import LLM
from pact_ai.prompts import STRUCTURE_SYSTEM, build_structure_contents
from pact_ai.schemas import AgreementDraft, AgreementExtraction, StructureAgreementOut
from pact_ai.services.agreement_output import build_structure_output
from pact_ai.services.caching import mark_cached


def structure_agreement(
    *,
    llm: LLM,
    cache: TTLCache,
    settings: Settings,
    text: str | None,
    previous: AgreementDraft | None,
    feedback: str | None,
    ingested: Ingested,
) -> StructureAgreementOut:
    key = make_key(
        "structure",
        settings.gemini_model,
        text,
        previous.model_dump() if previous else None,
        feedback,
        *ingested.fingerprint,
    )
    cached = cache.get(key)
    if cached is not None:
        return mark_cached(cached)

    contents = build_structure_contents(text, previous, feedback, ingested)
    try:
        extraction, meta = llm.generate(STRUCTURE_SYSTEM, contents, AgreementExtraction)
    except LLMUnavailable:
        if text and text.strip() and ingested.count == 0 and previous is None:
            return structure_from_rules(text)
        raise

    result = build_structure_output(extraction, meta, settings)
    cache.set(key, result)
    return result
