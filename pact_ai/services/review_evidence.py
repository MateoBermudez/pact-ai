from pact_ai.core.cache import TTLCache, make_key
from pact_ai.core.config import Settings
from pact_ai.core.errors import LLMUnavailable
from pact_ai.fallback import review_from_rules
from pact_ai.ingestion import Ingested
from pact_ai.llm.base import LLM
from pact_ai.prompts import REVIEW_SYSTEM, build_review_contents
from pact_ai.schemas import Meta, ReviewEvidenceOut, ReviewExtraction
from pact_ai.services.caching import mark_cached


def enforce_verdict(extraction: ReviewExtraction) -> str:
    all_met = bool(extraction.checklist) and all(item.met for item in extraction.checklist)
    return "cumple" if extraction.verdict == "cumple" and all_met else "revisar"


def build_review_output(extraction: ReviewExtraction, meta: Meta) -> ReviewEvidenceOut:
    return ReviewEvidenceOut(
        verdict=enforce_verdict(extraction),
        reason=extraction.reason.strip(),
        checklist=extraction.checklist,
        confidence=min(max(extraction.confidence, 0.0), 1.0),
        meta=meta,
    )


def review_evidence(
    *,
    llm: LLM,
    cache: TTLCache,
    settings: Settings,
    requirements: str,
    provider_note: str,
    evidence_url: str,
    ingested: Ingested,
) -> ReviewEvidenceOut:
    key = make_key(
        "review",
        settings.gemini_model,
        requirements,
        provider_note,
        evidence_url,
        *ingested.fingerprint,
    )
    cached = cache.get(key)
    if cached is not None:
        return mark_cached(cached)

    contents = build_review_contents(requirements, provider_note, evidence_url, ingested)
    try:
        extraction, meta = llm.generate(REVIEW_SYSTEM, contents, ReviewExtraction)
    except LLMUnavailable:
        return review_from_rules()

    result = build_review_output(extraction, meta)
    cache.set(key, result)
    return result
