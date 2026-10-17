from fastapi import APIRouter, Depends

from pact_ai.core.config import get_settings
from pact_ai.core.security import require_secret
from pact_ai.schemas import ScreenApplicantIn, ScreenApplicantOut
from pact_ai.services import screen_applicant

router = APIRouter(tags=["screening"], dependencies=[Depends(require_secret)])


@router.post("/screen-applicant", response_model=ScreenApplicantOut)
async def screen(body: ScreenApplicantIn) -> ScreenApplicantOut:
    return await screen_applicant(body, get_settings())
