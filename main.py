import base64
import binascii
import hmac
import os
import re
from typing import Annotated, TypeVar

from fastapi import Depends, FastAPI, Header, HTTPException
from google.genai import types
from pydantic import BaseModel, ValidationError

import gemini
from prompts import (
    REVIEW_SYSTEM,
    STRUCTURE_SYSTEM,
    review_prompt,
    structure_file_label,
    structure_prompt,
)
from schemas import (
    CATEGORIES,
    FileIn,
    ReviewDraft,
    ReviewEvidenceIn,
    ReviewEvidenceOut,
    RuleOut,
    RuleResultOut,
    StructureAgreementIn,
    StructureAgreementOut,
    StructureDraft,
)

T = TypeVar("T", bound=BaseModel)

TEXT_FILE_TYPES = {"text/plain", "text/markdown"}
BINARY_FILE_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
MAX_FILE_BYTES = 7 * 1024 * 1024
MAX_TEXT_FILE_CHARS = 20_000

app = FastAPI(title="PACT AI", version="0.2.0")


def require_secret(x_pact_ai_secret: Annotated[str | None, Header()] = None) -> None:
    """Si hay secreto compartido configurado, solo el servidor de Next.js (que lo conoce) puede usar este servicio."""
    expected = os.environ.get("PACT_AI_SHARED_SECRET")
    if not expected:
        return
    if not x_pact_ai_secret or not hmac.compare_digest(x_pact_ai_secret, expected):
        raise HTTPException(status_code=401, detail="No autorizado")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


async def generate(schema: type[T], system: str, contents: list[types.Part | str], timeout_seconds: float) -> T:
    try:
        return await gemini.generate_structured(
            system=system, contents=contents, schema=schema, timeout_seconds=timeout_seconds
        )
    except gemini.GeminiNotConfigured as error:
        raise HTTPException(status_code=503, detail="La IA no está configurada") from error
    except gemini.GeminiError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


def file_parts(file: FileIn) -> list[types.Part | str]:
    if file.mime_type not in TEXT_FILE_TYPES | BINARY_FILE_TYPES:
        raise HTTPException(status_code=415, detail=f"Tipo de archivo no admitido: {file.mime_type}")
    try:
        data = base64.b64decode(file.data_base64, validate=True)
    except (binascii.Error, ValueError) as error:
        raise HTTPException(status_code=422, detail="El archivo no es base64 válido") from error
    if not data or len(data) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="El archivo está vacío o supera 7 MB")

    label = structure_file_label(file.file_name)
    if file.mime_type in TEXT_FILE_TYPES:
        text = data.decode("utf-8", errors="replace")[:MAX_TEXT_FILE_CHARS]
        return [f"{label}\n{text}\n</archivo>"]
    return [label, types.Part.from_bytes(data=data, mime_type=file.mime_type), "</archivo>"]


def clean_keywords(keywords: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for keyword in keywords:
        cleaned = keyword.strip().lower()
        if cleaned and len(cleaned) <= 40:
            seen[cleaned] = None
    return list(seen)[:15]


def to_structure(draft: StructureDraft) -> StructureAgreementOut:
    rules = [
        RuleOut(criterion=rule.criterion.strip()[:300], weight=min(5, max(1, rule.weight)))
        for rule in draft.rules
        if len(rule.criterion.strip()) >= 3
    ][:8]
    category = draft.category if draft.category in CATEGORIES else None
    try:
        return StructureAgreementOut(
            title=draft.title.strip()[:120],
            description=draft.description.strip()[:5000],
            amount_mon=draft.amount_mon if draft.amount_mon and draft.amount_mon > 0 else None,
            days=draft.days if draft.days and draft.days > 0 else None,
            category=category,
            keywords=clean_keywords(draft.keywords),
            rules=rules,
        )
    except ValidationError as error:
        raise HTTPException(status_code=502, detail="La IA devolvió un acuerdo incompleto") from error


@app.post("/structure-agreement", response_model=StructureAgreementOut, dependencies=[Depends(require_secret)])
async def structure_agreement(body: StructureAgreementIn) -> StructureAgreementOut:
    contents: list[types.Part | str] = []
    if prompt := structure_prompt(body.text):
        contents.append(prompt)
    if body.file is not None:
        contents.extend(file_parts(body.file))

    draft = await generate(StructureDraft, STRUCTURE_SYSTEM, contents, timeout_seconds=40)
    return to_structure(draft)


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


UNVERIFIED = "La IA no evaluó esta regla; se cuenta como no cumplida."
NO_QUOTE = "No se encontró en la entrega la cita que respalda esta regla; se cuenta como no cumplida."


@app.post("/review-evidence", response_model=ReviewEvidenceOut, dependencies=[Depends(require_secret)])
async def review_evidence(body: ReviewEvidenceIn) -> ReviewEvidenceOut:
    draft = await generate(ReviewDraft, REVIEW_SYSTEM, [review_prompt(body)], timeout_seconds=25)

    delivery_text = _squash(f"{body.provider_note} {body.evidence_url}")
    by_position = {}
    for result in draft.results:
        by_position.setdefault(result.position, result)

    results: list[RuleResultOut] = []
    for rule in body.rules:
        result = by_position.get(rule.position)
        if result is None:
            results.append(RuleResultOut(position=rule.position, met=False, reasoning=UNVERIFIED, evidence_excerpt=None))
            continue

        excerpt = (result.evidence_excerpt or "").strip()
        quoted = bool(excerpt) and _squash(excerpt) in delivery_text
        met = result.met and quoted
        reasoning = result.reasoning.strip()[:1000] or "Sin explicación"
        if result.met and not quoted:
            reasoning = f"{NO_QUOTE} ({reasoning[:300]})"
        results.append(
            RuleResultOut(
                position=rule.position,
                met=met,
                reasoning=reasoning,
                evidence_excerpt=excerpt[:500] if quoted else None,
            )
        )

    return ReviewEvidenceOut(
        summary=draft.summary.strip()[:2000] or "Sin resumen",
        results=results,
        model=gemini.model_name(),
    )
