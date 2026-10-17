from pact_ai.core.config import get_settings
from pact_ai.services.agreement_output import (
    fit_bytes,
    normalize_amount,
    normalize_days,
)


def test_fit_bytes_keeps_short_text():
    assert fit_bytes("hola   mundo", 500) == "hola mundo"


def test_fit_bytes_respects_utf8_limit():
    result = fit_bytes("ñandú " * 200, 100)
    assert len(result.encode()) <= 100
    assert result.endswith("…")


def test_normalize_amount_rounds_and_caps():
    settings = get_settings()
    warnings: list[str] = []
    assert normalize_amount(1.23456789, settings, warnings) == 1.2346
    assert normalize_amount(settings.max_amount_mon + 1, settings, warnings) is None
    assert warnings
    assert normalize_amount(None, settings, warnings) is None
    assert normalize_amount(0, settings, warnings) is None


def test_normalize_days_range():
    assert normalize_days(5) == 5
    assert normalize_days(0) is None
    assert normalize_days(366) is None
    assert normalize_days(None) is None
