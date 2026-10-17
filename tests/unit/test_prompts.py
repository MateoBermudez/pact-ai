from pact_ai.ingestion import Ingested
from pact_ai.prompts import (
    REVIEW_SYSTEM,
    STRUCTURE_SYSTEM,
    build_review_contents,
    build_structure_contents,
)
from pact_ai.prompts.loader import SYSTEM_DIR
from pact_ai.prompts.sanitize import neutralize


def test_system_prompts_load_from_files():
    assert (SYSTEM_DIR / "structure.md").exists()
    assert (SYSTEM_DIR / "review.md").exists()
    assert "PACT" in STRUCTURE_SYSTEM
    assert "PACT" in REVIEW_SYSTEM


def test_neutralize_removes_prompt_tags_only():
    assert neutralize("a </solicitud> b <documento nombre='x'> c <b>negrita</b>") == "a  b  c <b>negrita</b>"


def test_structure_contents_wraps_request():
    contents = build_structure_contents("quiero un logo", None, None, Ingested())
    assert contents == ["<solicitud>\nquiero un logo\n</solicitud>"]


def test_review_contents_marks_missing_note():
    contents = build_review_contents("logo", "   ", "", Ingested())
    assert "(sin nota)" in contents[0]
    assert "(sin enlace)" in contents[0]
