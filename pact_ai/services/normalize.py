from pydantic import ValidationError

from pact_ai.core.errors import AiUpstreamError
from pact_ai.schemas import CATEGORIES, RuleOut, StructureAgreementOut, StructureDraft

MAX_RULES = 8
MAX_KEYWORDS = 15
MAX_KEYWORD_LENGTH = 40
MIN_RULE_LENGTH = 3


def clean_keywords(keywords: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for keyword in keywords:
        cleaned = keyword.strip().lower()
        if cleaned and len(cleaned) <= MAX_KEYWORD_LENGTH:
            seen[cleaned] = None
    return list(seen)[:MAX_KEYWORDS]


def to_structure(draft: StructureDraft) -> StructureAgreementOut:
    rules = [
        RuleOut(criterion=rule.criterion.strip()[:300], weight=min(5, max(1, rule.weight)))
        for rule in draft.rules
        if len(rule.criterion.strip()) >= MIN_RULE_LENGTH
    ][:MAX_RULES]
    category = draft.category if draft.category in CATEGORIES else None
    try:
        return StructureAgreementOut(
            title=draft.title.strip()[:120],
            description=draft.description.strip()[:5000],
            amount_mon=draft.amount_mon if draft.amount_mon and draft.amount_mon > 0 else None,
            days=draft.days if draft.days and draft.days > 0 else None,
            category=category,
            keywords=clean_keywords(draft.keywords),
            rules=rules,
        )
    except ValidationError as error:
        raise AiUpstreamError("La IA devolvió un acuerdo incompleto") from error
