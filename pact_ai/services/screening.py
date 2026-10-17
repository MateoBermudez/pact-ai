from pact_ai.core.config import Settings
from pact_ai.prompts import SCREENING_SYSTEM, screening_prompt
from pact_ai.schemas import ScreenApplicantIn, ScreenApplicantOut, ScreeningDraft, Verdict
from pact_ai.services.generation import generate

ACCEPT_MIN_SCORE = 70
REJECT_MAX_SCORE = 45
MAX_POINTS = 4
MAX_POINT_LENGTH = 200


def _points(items: list[str]) -> list[str]:
    return [item.strip()[:MAX_POINT_LENGTH] for item in items if item.strip()][:MAX_POINTS]


def consistent_verdict(verdict: Verdict, score: int) -> Verdict:
    if verdict == "accept" and score < ACCEPT_MIN_SCORE:
        return "review"
    if verdict == "reject" and score > REJECT_MAX_SCORE:
        return "review"
    return verdict


async def screen_applicant(body: ScreenApplicantIn, settings: Settings) -> ScreenApplicantOut:
    generation = await generate(ScreeningDraft, SCREENING_SYSTEM, [screening_prompt(body)], settings.screening_timeout_seconds)
    draft = generation.parsed
    score = min(100, max(0, draft.score))
    return ScreenApplicantOut(
        verdict=consistent_verdict(draft.verdict, score),
        score=score,
        summary=draft.summary.strip()[:1000] or "Sin resumen",
        strengths=_points(draft.strengths),
        concerns=_points(draft.concerns),
        model=generation.model,
    )
