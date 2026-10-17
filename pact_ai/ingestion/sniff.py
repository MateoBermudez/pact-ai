import io
import zipfile

PDF = "application/pdf"
PNG = "image/png"
JPEG = "image/jpeg"
WEBP = "image/webp"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
TEXT_TYPES = frozenset({"text/plain", "text/markdown"})
BINARY_TYPES = frozenset({PDF, PNG, JPEG, WEBP})
ACCEPTED_TYPES = TEXT_TYPES | BINARY_TYPES | {DOCX}


def is_docx(data: bytes) -> bool:
    if not data.startswith(b"PK"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            return "word/document.xml" in archive.namelist()
    except zipfile.BadZipFile:
        return False


def matches_type(mime_type: str, data: bytes) -> bool:
    if mime_type == PDF:
        return data.startswith(b"%PDF")
    if mime_type == PNG:
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if mime_type == JPEG:
        return data.startswith(b"\xff\xd8\xff")
    if mime_type == WEBP:
        return data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if mime_type == DOCX:
        return is_docx(data)
    return True
