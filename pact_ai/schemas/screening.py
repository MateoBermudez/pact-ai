from typing import Literal

from pydantic import BaseModel, Field

Verdict = Literal["accept", "review", "reject"]


class ListingIn(BaseModel):
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=5000)
    category: str | None = Field(default=None, max_length=60)
    keywords: list[str] = Field(default_factory=list, max_length=40)
    budget_mon: float | None = Field(default=None, gt=0)
    deadline_days: int | None = Field(default=None, gt=0)
    rules: list[str] = Field(default_factory=list, max_length=12)


class PortfolioItemIn(BaseModel):
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    url: str | None = Field(default=None, max_length=512)


class ApplicantIn(BaseModel):
    display_name: str = Field(default="", max_length=120)
    bio: str = Field(default="", max_length=2000)
    skills: list[str] = Field(default_factory=list, max_length=60)
    keywords: list[str] = Field(default_factory=list, max_length=60)
    availability: str | None = Field(default=None, max_length=40)
    provider_score: float | None = Field(default=None, ge=0, le=5)
    completed_jobs: int = Field(default=0, ge=0)
    portfolio: list[PortfolioItemIn] = Field(default_factory=list, max_length=20)


class ProposalIn(BaseModel):
    message: str = Field(max_length=2000)
    price_mon: float | None = Field(default=None, gt=0)
    days: int | None = Field(default=None, gt=0)


class ScreenApplicantIn(BaseModel):
    listing: ListingIn
    applicant: ApplicantIn
    proposal: ProposalIn
    client_preferences: str = Field(default="", max_length=1000, description="Criterios propios del cliente")


class ScreenApplicantOut(BaseModel):
    verdict: Verdict
    score: int = Field(ge=0, le=100)
    summary: str = Field(min_length=1, max_length=1000)
    strengths: list[str] = Field(max_length=6)
    concerns: list[str] = Field(max_length=6)
    model: str


class ScreeningDraft(BaseModel):
    verdict: Verdict
    score: int
    summary: str
    strengths: list[str]
    concerns: list[str]
