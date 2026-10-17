import re

AMOUNT_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:mon|usdc|usdt|usd|d[oó]lares?|eth)\b",
    re.IGNORECASE,
)
DAYS_PATTERN = re.compile(r"(\d+)\s*(d[ií]as?|semanas?|meses|mes)\b", re.IGNORECASE)
UNIT_DAYS = {"d": 1, "s": 7, "m": 30}


def parse_amount(text: str) -> float | None:
    match = AMOUNT_PATTERN.search(text)
    if not match:
        return None
    value = float(match.group(1).replace(",", "."))
    return value if value > 0 else None


def parse_days(text: str) -> int | None:
    match = DAYS_PATTERN.search(text)
    if not match:
        return None
    unit = match.group(2)[0].lower()
    return int(match.group(1)) * UNIT_DAYS[unit] or None
