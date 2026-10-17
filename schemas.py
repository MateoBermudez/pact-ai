from typing import Self

from pydantic import BaseModel, Field, model_validator

CATEGORIES = ("Diseño", "Contenido", "Marketing", "Programación", "Blockchain", "Datos e IA", "Otro")


class FileIn(BaseModel):
    file_name: str = Field(min_length=1, max_length=200)
    mime_type: str = Field(min_length=1, max_length=100)
    data_base64: str = Field(min_length=1)


class StructureAgreementIn(BaseModel):
    text: str | None = Field(default=None, max_length=5000, description="Texto tal cual lo escribe el cliente")
    file: FileIn | None = Field(default=None, description="Brief adjunto (PDF, imagen o texto)")

    @model_validator(mode="after")
    def requires_text_or_file(self) -> Self:
        if not (self.text and self.text.strip()) and self.file is None:
            raise ValueError("Envía un texto, un archivo o ambos")
        return self


class RuleOut(BaseModel):
    criterion: str = Field(min_length=3, max_length=300)
    weight: int = Field(ge=1, le=5)


class StructureAgreementOut(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=5000)
    amount_mon: float | None = Field(gt=0)
    days: int | None = Field(gt=0)
    category: str | None
    keywords: list[str] = Field(max_length=15)
    rules: list[RuleOut] = Field(min_length=1, max_length=8)


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


# Esquemas que se le piden al modelo: tipos simples, sin restricciones que el esquema de Gemini no admite.
# Lo que devuelve se valida después contra los modelos de arriba.
class RuleDraft(BaseModel):
    criterion: str
    weight: int


class StructureDraft(BaseModel):
    title: str
    description: str
    amount_mon: float | None
    days: int | None
    category: str | None
    keywords: list[str]
    rules: list[RuleDraft]


class ResultDraft(BaseModel):
    position: int
    met: bool
    reasoning: str
    evidence_excerpt: str | None


class ReviewDraft(BaseModel):
    summary: str
    results: list[ResultDraft]
