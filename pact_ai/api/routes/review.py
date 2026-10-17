from fastapi import APIRouter, Depends

from pact_ai.core.config import get_settings
from pact_ai.core.security import require_secret
from pact_ai.schemas import ReviewEvidenceIn, ReviewEvidenceOut
from pact_ai.services import review_evidence

router = APIRouter(tags=["review"], dependencies=[Depends(require_secret)])


@router.post("/review-evidence", response_model=ReviewEvidenceOut)
async def review(body: ReviewEvidenceIn) -> ReviewEvidenceOut:
    return await review_evidence(body, get_settings())
