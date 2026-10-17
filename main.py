from fastapi import FastAPI, HTTPException

from schemas import (
    ReviewEvidenceIn,
    ReviewEvidenceOut,
    StructureAgreementIn,
    StructureAgreementOut,
)

app = FastAPI(title="PACT AI", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/structure-agreement", response_model=StructureAgreementOut)
def structure_agreement(body: StructureAgreementIn) -> StructureAgreementOut:
    raise HTTPException(status_code=501, detail="Pendiente: llamada a Gemini (entregable D)")


@app.post("/review-evidence", response_model=ReviewEvidenceOut)
def review_evidence(body: ReviewEvidenceIn) -> ReviewEvidenceOut:
    raise HTTPException(status_code=501, detail="Pendiente: llamada a Gemini (entregable D)")
