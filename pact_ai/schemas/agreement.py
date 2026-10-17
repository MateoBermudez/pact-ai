from typing import Literal

from pydantic import BaseModel, Field, model_validator

from pact_ai.schemas.common import Meta

Category = Literal[
    "diseño",
    "desarrollo",
    "marketing",
    "redacción",
    "traducción",
    "video",
    "datos",
    "consultoría",
    "otro",
]


class AgreementDraft(BaseModel):
    description: str = Field(max_length=2000)
    amount_mon: float = Field(gt=0)
    days: int = Field(gt=0)
    title: str = ""
    deliverables: list[str] = []
    acceptance_criteria: list[str] = []
    category: str = ""
    skills: list[str] = []
    suggested_milestones: list[str] = []


class StructureAgreementIn(BaseModel):
    text: str | None = Field(default=None, max_length=8000, description="Texto tal cual lo escribe el cliente")
    previous: AgreementDraft | None = Field(default=None, description="Borrador anterior a refinar")
    feedback: str | None = Field(default=None, max_length=1000, description="Cambio que pide el cliente sobre el borrador")

    @model_validator(mode="after")
    def has_input(self) -> "StructureAgreementIn":
        has_text = bool(self.text and self.text.strip())
        has_refinement = self.previous is not None and bool(self.feedback and self.feedback.strip())
        if not has_text and not has_refinement:
            raise ValueError("Se requiere text, o previous junto con feedback")
        return self


class AgreementExtraction(BaseModel):
    description: str
    amount_mon: float | None
    days: int | None
    title: str
    deliverables: list[str]
    acceptance_criteria: list[str]
    category: Category
    skills: list[str]
    suggested_milestones: list[str]
    warnings: list[str]
    questions: list[str]


class StructureAgreementOut(BaseModel):
    status: Literal["ok", "needs_clarification"]
    description: str
    amount_mon: float | None
    days: int | None
    title: str = ""
    deliverables: list[str] = []
    acceptance_criteria: list[str] = []
    category: str = ""
    skills: list[str] = []
    suggested_milestones: list[str] = []
    warnings: list[str] = []
    questions: list[str] = []
    meta: Meta
