from pydantic import BaseModel, Field


class RuleIn(BaseModel):
    position: int = Field(ge=1)
    criterion: str = Field(min_length=1, max_length=300)
    weight: int = Field(ge=1, le=5)


class ReviewEvidenceIn(BaseModel):
    requirements: str = Field(max_length=5000, description="Descripción original del acuerdo")
    rules: list[RuleIn] = Field(min_length=1, max_length=12, description="Reglas de aceptación confirmadas")
    provider_note: str = Field(max_length=2000, description="Nota que escribió el proveedor al entregar")
    evidence_url: str = Field(max_length=512, description="Enlace de la entrega; no se abre, solo se lee el texto")


class RuleResultOut(BaseModel):
    position: int
    met: bool
    reasoning: str
    evidence_excerpt: str | None


class ReviewEvidenceOut(BaseModel):
    summary: str
    results: list[RuleResultOut]
    model: str


class ResultDraft(BaseModel):
    position: int
    met: bool
    reasoning: str
    evidence_excerpt: str | None


class ReviewDraft(BaseModel):
    summary: str
    results: list[ResultDraft]
