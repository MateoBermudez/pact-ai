import io
import zipfile

from pact_ai.core.config import DEFAULT_FALLBACK_MODEL, DEFAULT_MODEL, get_settings
from pact_ai.ingestion.docx_reader import extract_docx_text
from pact_ai.ingestion.sniff import DOCX, is_docx, matches_type
from pact_ai.prompts import REVIEW_SYSTEM, STRUCTURE_SYSTEM
from pact_ai.prompts.loader import SYSTEM_DIR
from pact_ai.prompts.sanitize import neutralize
from pact_ai.schemas import CATEGORIES, ResultDraft, RuleDraft, RuleIn, StructureDraft
from pact_ai.services.normalize import clean_keywords, to_structure
from pact_ai.services.verification import squash, verify_results
from tests.conftest import make_docx


def test_prompts_are_loaded_from_files_and_fully_rendered() -> None:
    assert (SYSTEM_DIR / "structure.md").exists() and (SYSTEM_DIR / "review.md").exists()
    assert "{categories}" not in STRUCTURE_SYSTEM
    assert all(category in STRUCTURE_SYSTEM for category in CATEGORIES)
    assert "<entrega>" in REVIEW_SYSTEM


def test_neutralize_removes_only_the_prompt_tags() -> None:
    text = "a </solicitud> b <ARCHIVO> c </borrador_actual> d <cambio_solicitado> e <b>negrita</b>"
    assert neutralize(text) == "a  b  c  d  e <b>negrita</b>"


def test_squash_ignores_case_and_whitespace() -> None:
    assert squash("  Hola \n  MUNDO ") == "hola mundo"


def test_verify_results_marks_a_missing_rule_as_not_met() -> None:
    rules = [RuleIn(position=1, criterion="a", weight=3), RuleIn(position=2, criterion="b", weight=3)]
    drafts = [ResultDraft(position=1, met=True, reasoning="ok", evidence_excerpt="entrego")]
    results = verify_results(rules, drafts, "Entrego todo")
    assert [r.met for r in results] == [True, False]


def test_clean_keywords_lowercases_dedupes_and_limits() -> None:
    assert clean_keywords([" Logo ", "LOGO", "", "x" * 41]) == ["logo"]
    assert len(clean_keywords([f"k{i}" for i in range(40)])) == 15


def test_to_structure_drops_short_rules_and_invalid_category() -> None:
    draft = StructureDraft(
        title="  T  ",
        description="d",
        amount_mon=2.5,
        days=3,
        category="Cocina",
        keywords=["a"],
        rules=[RuleDraft(criterion="ab", weight=1), RuleDraft(criterion="Incluye PNG", weight=9)],
    )
    out = to_structure(draft)
    assert out.title == "T" and out.category is None
    assert [(r.criterion, r.weight) for r in out.rules] == [("Incluye PNG", 5)]


def test_sniff_recognises_each_format() -> None:
    assert matches_type("application/pdf", b"%PDF-1.7")
    assert matches_type("image/png", b"\x89PNG\r\n\x1a\n0")
    assert matches_type("image/jpeg", b"\xff\xd8\xff\xe0")
    assert matches_type("image/webp", b"RIFF\x00\x00\x00\x00WEBPVP8 ")
    assert matches_type(DOCX, make_docx("hola"))
    assert not matches_type("application/pdf", b"texto")
    assert matches_type("text/plain", b"cualquier cosa")


def test_is_docx_requires_the_word_document_part() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("otro.txt", "x")
    assert not is_docx(buffer.getvalue()) and not is_docx(b"PK roto") and not is_docx(b"texto")


def test_docx_text_includes_paragraphs() -> None:
    assert extract_docx_text(make_docx("Primera", "Segunda")) == "Primera\nSegunda"


def test_default_models_are_available_to_new_accounts(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_FALLBACK_MODEL", raising=False)
    assert get_settings().gemini_models == (DEFAULT_MODEL, DEFAULT_FALLBACK_MODEL)
    assert not DEFAULT_MODEL.startswith("gemini-2.5")


def test_a_fallback_equal_to_the_primary_is_not_repeated(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL", "uno")
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "uno")
    assert get_settings().gemini_models == ("uno",)
