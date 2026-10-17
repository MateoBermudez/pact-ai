from fastapi import HTTPException, UploadFile
from pydantic import ValidationError

from pact_ai.core.config import Settings
from pact_ai.schemas import AgreementDraft


async def read_uploads(uploads: list[UploadFile] | None, settings: Settings) -> list[tuple[str, bytes]]:
    files: list[tuple[str, bytes]] = []
    for upload in uploads or []:
        if not upload.filename:
            continue
        data = await upload.read(settings.max_file_bytes + 1)
        files.append((upload.filename, data))
    return files


def parse_draft(raw: str | None) -> AgreementDraft | None:
    if raw is None or not raw.strip():
        return None
    try:
        return AgreementDraft.model_validate_json(raw)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="previous no es un borrador válido") from exc
