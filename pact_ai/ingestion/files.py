import base64
import binascii

from google.genai import types

from pact_ai.core.config import Settings
from pact_ai.core.errors import FileRejected
from pact_ai.ingestion.docx_reader import extract_docx_text
from pact_ai.ingestion.sniff import ACCEPTED_TYPES, DOCX, TEXT_TYPES, matches_type
from pact_ai.prompts import structure_file_label
from pact_ai.schemas import FileIn


def decode_file(file: FileIn, settings: Settings) -> bytes:
    if file.mime_type not in ACCEPTED_TYPES:
        raise FileRejected(415, f"Tipo de archivo no admitido: {file.mime_type}")
    try:
        data = base64.b64decode(file.data_base64, validate=True)
    except (binascii.Error, ValueError) as error:
        raise FileRejected(422, "El archivo no es base64 válido") from error
    if not data or len(data) > settings.max_file_bytes:
        raise FileRejected(413, "El archivo está vacío o supera el tamaño máximo")
    if not matches_type(file.mime_type, data):
        raise FileRejected(415, "El contenido del archivo no coincide con su tipo")
    return data


def file_contents(file: FileIn, settings: Settings) -> list[types.Part | str]:
    data = decode_file(file, settings)
    label = structure_file_label(file.file_name)

    if file.mime_type in TEXT_TYPES:
        text = data.decode("utf-8", errors="replace")[: settings.max_text_file_chars]
        return [f"{label}\n{text}\n</archivo>"]

    if file.mime_type == DOCX:
        try:
            text = extract_docx_text(data)
        except Exception as error:
            raise FileRejected(422, "No se pudo leer el DOCX") from error
        if not text.strip():
            raise FileRejected(422, "El DOCX no contiene texto legible")
        return [f"{label}\n{text[: settings.max_text_file_chars]}\n</archivo>"]

    return [label, types.Part.from_bytes(data=data, mime_type=file.mime_type), "</archivo>"]
