import re

from google.genai import types

from pact_ai.core.config import Settings
from pact_ai.core.errors import FileRejected
from pact_ai.ingestion.docx_reader import extract_docx_text
from pact_ai.ingestion.models import Ingested
from pact_ai.ingestion.sniff import decode_text, detect_image_mime, is_docx, is_pdf

UNSUPPORTED_REASON = "formato no soportado (use PDF, DOCX, PNG, JPG, WEBP, TXT o MD)"


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^\w.\- ]", "_", name or "archivo")
    return cleaned[:80] or "archivo"


def check_limits(files: list[tuple[str, bytes]], settings: Settings) -> None:
    if len(files) > settings.max_files:
        raise FileRejected("archivos", f"máximo {settings.max_files} archivos", 413)
    if sum(len(data) for _, data in files) > settings.max_total_bytes:
        raise FileRejected("archivos", "el tamaño total supera el máximo permitido", 413)


def ingest_one(name: str, data: bytes, settings: Settings, into: Ingested) -> None:
    if not data:
        raise FileRejected(name, "archivo vacío", 400)
    if len(data) > settings.max_file_bytes:
        raise FileRejected(name, "supera el tamaño máximo por archivo", 413)

    into.fingerprint.append(data)

    if is_pdf(data):
        into.parts.append(types.Part.from_bytes(data=data, mime_type="application/pdf"))
        return

    image_mime = detect_image_mime(data)
    if image_mime:
        into.parts.append(types.Part.from_bytes(data=data, mime_type=image_mime))
        return

    if is_docx(data):
        try:
            text = extract_docx_text(data)
        except Exception as exc:
            raise FileRejected(name, "no se pudo leer el DOCX", 422) from exc
        if not text.strip():
            raise FileRejected(name, "el DOCX no contiene texto legible", 422)
        into.documents.append((name, text[: settings.max_document_chars]))
        return

    text = decode_text(data)
    if text is not None and text.strip():
        into.documents.append((name, text[: settings.max_document_chars]))
        return

    raise FileRejected(name, UNSUPPORTED_REASON)


def ingest_files(files: list[tuple[str, bytes]], settings: Settings) -> Ingested:
    check_limits(files, settings)
    result = Ingested()
    for raw_name, data in files:
        ingest_one(safe_name(raw_name), data, settings, result)
    return result
