import pytest

from pact_ai.core.config import get_settings
from pact_ai.core.errors import FileRejected
from pact_ai.ingestion import ingest_files
from pact_ai.ingestion.ingest import safe_name
from pact_ai.ingestion.sniff import decode_text, detect_image_mime, is_docx, is_pdf
from tests.helpers import PDF_BYTES, PNG_BYTES, make_docx


def test_sniff_detects_each_format():
    assert is_pdf(PDF_BYTES)
    assert detect_image_mime(PNG_BYTES) == "image/png"
    assert detect_image_mime(b"\xff\xd8\xff\xe0" + b"0" * 8) == "image/jpeg"
    assert detect_image_mime(b"RIFF\x00\x00\x00\x00WEBPVP8 ") == "image/webp"
    assert is_docx(make_docx("hola"))
    assert not is_docx(b"PK\x03\x04no es docx")
    assert decode_text(b"\x00\x01binary") is None
    assert decode_text("ñandú".encode()) == "ñandú"


def test_ingest_classifies_files():
    settings = get_settings()
    result = ingest_files(
        [
            ("brief.pdf", PDF_BYTES),
            ("logo.png", PNG_BYTES),
            ("notas.txt", b"notas libres"),
        ],
        settings,
    )
    assert len(result.parts) == 2
    assert result.documents == [("notas.txt", "notas libres")]
    assert result.count == 3
    assert len(result.fingerprint) == 3


def test_ingest_extracts_docx_text():
    result = ingest_files([("alcance.docx", make_docx("Alcance del proyecto"))], get_settings())
    assert result.documents == [("alcance.docx", "Alcance del proyecto")]
    assert not result.parts


def test_ingest_rejects_empty_file():
    with pytest.raises(FileRejected) as exc:
        ingest_files([("vacio.txt", b"")], get_settings())
    assert exc.value.status_code == 400


def test_safe_name_strips_unsafe_characters():
    assert safe_name('a"<b>.pdf') == "a__b_.pdf"
    assert safe_name("") == "archivo"
