import pytest

from pact_ai.fallback.parsing import parse_amount, parse_days
from pact_ai.fallback.rules import review_from_rules, structure_from_rules


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("pagaré 10 MON", 10),
        ("pago 2,5 usdc", 2.5),
        ("son 25 dólares", 25),
        ("sin monto", None),
    ],
)
def test_parse_amount(text, expected):
    assert parse_amount(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("en 5 días", 5),
        ("en 2 semanas", 14),
        ("en 1 mes", 30),
        ("sin plazo", None),
    ],
)
def test_parse_days(text, expected):
    assert parse_days(text) == expected


def test_structure_from_rules_marks_missing_fields():
    out = structure_from_rules("necesito un logo")
    assert out.status == "needs_clarification"
    assert len(out.questions) == 2
    assert out.meta.source == "fallback"


def test_review_from_rules_is_conservative():
    assert review_from_rules().verdict == "revisar"
