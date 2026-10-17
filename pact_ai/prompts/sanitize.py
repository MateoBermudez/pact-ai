import re

TAG_PATTERN = re.compile(
    r"</?\s*(solicitud|documento|borrador_actual|cambio_solicitado|requisitos|nota_proveedor|enlace_evidencia)\b[^>]*>",
    re.IGNORECASE,
)


def neutralize(text: str) -> str:
    return TAG_PATTERN.sub("", text)
