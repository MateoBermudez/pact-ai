from typing import Literal

from pydantic import BaseModel, Field


class StructureAgreementIn(BaseModel):
    text: str = Field(min_length=1, description="Texto tal cual lo escribe el cliente")


class StructureAgreementOut(BaseModel):
    description: str
    amount_mon: float = Field(gt=0)
    days: int = Field(gt=0)


class ReviewEvidenceIn(BaseModel):
    requirements: str = Field(description="Descripción original del acuerdo")
    provider_note: str = Field(description="Nota corta que escribió el proveedor al entregar")
    evidence_url: str = Field(description="Enlace de evidencia; no se abre, solo se compara el texto")


class ReviewEvidenceOut(BaseModel):
    verdict: Literal["cumple", "revisar"]
    reason: str
