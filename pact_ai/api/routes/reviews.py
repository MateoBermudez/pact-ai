from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from pact_ai import services
from pact_ai.api.uploads import read_uploads
from pact_ai.core.dependencies import CacheDep, LLMDep, Protected, SettingsDep
from pact_ai.ingestion import Ingested, ingest_files
from pact_ai.schemas import ReviewEvidenceIn, ReviewEvidenceOut

router = APIRouter(tags=["reviews"], dependencies=[Protected])


@router.post("/review-evidence", response_model=ReviewEvidenceOut)
def review_evidence(
    body: ReviewEvidenceIn, llm: LLMDep, cache: CacheDep, settings: SettingsDep
) -> ReviewEvidenceOut:
    return services.review_evidence(
        llm=llm,
        cache=cache,
        settings=settings,
        requirements=body.requirements,
        provider_note=body.provider_note,
        evidence_url=body.evidence_url,
        ingested=Ingested(),
    )


@router.post("/review-evidence/files", response_model=ReviewEvidenceOut)
async def review_evidence_files(
    llm: LLMDep,
    cache: CacheDep,
    settings: SettingsDep,
    requirements: Annotated[str, Form(min_length=1, max_length=4000)],
    provider_note: Annotated[str, Form(max_length=2000)] = "",
    evidence_url: Annotated[str, Form(max_length=2048)] = "",
    files: Annotated[list[UploadFile] | None, File()] = None,
) -> ReviewEvidenceOut:
    ingested = ingest_files(await read_uploads(files, settings), settings)
    return services.review_evidence(
        llm=llm,
        cache=cache,
        settings=settings,
        requirements=requirements,
        provider_note=provider_note,
        evidence_url=evidence_url,
        ingested=ingested,
    )
