import re

CLOSING_TAGS = re.compile(
    r"</?\s*(solicitud|archivo|entrega|contenido_entrega|reglas|requisitos|borrador_actual|cambio_solicitado|oportunidad|candidato|propuesta|criterios_del_cliente)\s*>",
    re.IGNORECASE,
)


def neutralize(text: str) -> str:
    return CLOSING_TAGS.sub("", text)
