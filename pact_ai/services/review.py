from pact_ai.core.config import Settings
from pact_ai.prompts import REVIEW_SYSTEM, review_prompt
from pact_ai.schemas import ReviewDraft, ReviewEvidenceIn, ReviewEvidenceOut
from pact_ai.services.generation import generate
from pact_ai.services.verification import verify_results


async def review_evidence(body: ReviewEvidenceIn, settings: Settings) -> ReviewEvidenceOut:
    generation = await generate(ReviewDraft, REVIEW_SYSTEM, [review_prompt(body)], settings.review_timeout_seconds)
    draft = generation.parsed

    delivery_text = f"{body.provider_note} {body.evidence_url} {body.evidence_text or ''}"
    return ReviewEvidenceOut(
        summary=draft.summary.strip()[:2000] or "Sin resumen",
        results=verify_results(body.rules, draft.results, delivery_text),
        model=generation.model,
    )
