from fastapi import APIRouter, Depends

from pact_ai.core.config import get_settings
from pact_ai.core.security import require_secret
from pact_ai.schemas import StructureAgreementIn, StructureAgreementOut
from pact_ai.services import structure_agreement

router = APIRouter(tags=["structure"], dependencies=[Depends(require_secret)])


@router.post("/structure-agreement", response_model=StructureAgreementOut)
async def structure(body: StructureAgreementIn) -> StructureAgreementOut:
    return await structure_agreement(body, get_settings())
