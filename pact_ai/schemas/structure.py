from typing import Self

from pydantic import BaseModel, Field, model_validator

from pact_ai.schemas.files import FileIn

CATEGORIES = ("Diseño", "Contenido", "Marketing", "Programación", "Blockchain", "Datos e IA", "Otro")


class RuleOut(BaseModel):
    criterion: str = Field(min_length=3, max_length=300)
    weight: int = Field(ge=1, le=5)


class PreviousRule(BaseModel):
    criterion: str = Field(min_length=1, max_length=300)
    weight: int = Field(default=3, ge=1, le=5)


class PreviousAgreement(BaseModel):
    title: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=5000)
    amount_mon: float | None = Field(default=None, gt=0)
    days: int | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, max_length=60)
    keywords: list[str] = Field(default_factory=list, max_length=40)
    rules: list[PreviousRule] = Field(default_factory=list, max_length=12)


class StructureAgreementIn(BaseModel):
    text: str | None = Field(default=None, max_length=5000, description="Texto tal cual lo escribe el cliente")
    file: FileIn | None = Field(default=None, description="Brief adjunto (PDF, DOCX, imagen o texto)")
    previous: PreviousAgreement | None = Field(default=None, description="Borrador anterior que se quiere ajustar")
    feedback: str | None = Field(default=None, max_length=1000, description="Cambio que pide el cliente sobre el borrador")

    @model_validator(mode="after")
    def requires_input(self) -> Self:
        has_text = bool(self.text and self.text.strip())
        has_refinement = self.previous is not None and bool(self.feedback and self.feedback.strip())
        if not has_text and self.file is None and not has_refinement:
            raise ValueError("Envía un texto, un archivo, o un borrador con el cambio que quieres")
        return self


class StructureAgreementOut(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=5000)
    amount_mon: float | None = Field(gt=0)
    days: int | None = Field(gt=0)
    category: str | None
    keywords: list[str] = Field(max_length=15)
    rules: list[RuleOut] = Field(min_length=1, max_length=8)


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
