from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from pact_ai import services
from pact_ai.api.uploads import parse_draft, read_uploads
from pact_ai.core.dependencies import CacheDep, LLMDep, Protected, SettingsDep
from pact_ai.ingestion import Ingested, ingest_files
from pact_ai.schemas import StructureAgreementIn, StructureAgreementOut

router = APIRouter(tags=["agreements"], dependencies=[Protected])


@router.post("/structure-agreement", response_model=StructureAgreementOut)
def structure_agreement(
    body: StructureAgreementIn, llm: LLMDep, cache: CacheDep, settings: SettingsDep
) -> StructureAgreementOut:
    return services.structure_agreement(
        llm=llm,
        cache=cache,
        settings=settings,
        text=body.text,
        previous=body.previous,
        feedback=body.feedback,
        ingested=Ingested(),
    )


@router.post("/structure-agreement/files", response_model=StructureAgreementOut)
async def structure_agreement_files(
    llm: LLMDep,
    cache: CacheDep,
    settings: SettingsDep,
    text: Annotated[str | None, Form(max_length=8000)] = None,
    previous: Annotated[str | None, Form()] = None,
    feedback: Annotated[str | None, Form(max_length=1000)] = None,
    files: Annotated[list[UploadFile] | None, File()] = None,
) -> StructureAgreementOut:
    ingested = ingest_files(await read_uploads(files, settings), settings)
    draft = parse_draft(previous)
    has_text = bool(text and text.strip())
    has_refinement = draft is not None and bool(feedback and feedback.strip())
    if not has_text and not has_refinement and ingested.count == 0:
        raise HTTPException(status_code=422, detail="Se requiere text, archivos, o previous junto con feedback")
    return services.structure_agreement(
        llm=llm,
        cache=cache,
        settings=settings,
        text=text,
        previous=draft,
        feedback=feedback,
        ingested=ingested,
    )
