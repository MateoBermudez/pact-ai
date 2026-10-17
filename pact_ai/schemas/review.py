from typing import Literal

from pydantic import BaseModel, Field

from pact_ai.schemas.common import Meta


class ReviewEvidenceIn(BaseModel):
    requirements: str = Field(min_length=1, max_length=4000, description="Descripción original del acuerdo")
    provider_note: str = Field(default="", max_length=2000, description="Nota corta que escribió el proveedor al entregar")
    evidence_url: str = Field(default="", max_length=2048, description="Enlace de evidencia; no se abre, solo se compara el texto")


class ChecklistItem(BaseModel):
    criterion: str
    met: bool
    comment: str


class ReviewExtraction(BaseModel):
    verdict: Literal["cumple", "revisar"]
    reason: str
    checklist: list[ChecklistItem]
    confidence: float


class ReviewEvidenceOut(BaseModel):
    verdict: Literal["cumple", "revisar"]
    reason: str
    checklist: list[ChecklistItem] = []
    confidence: float = 0.0
    meta: Meta
