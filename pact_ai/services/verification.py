import re

from pact_ai.schemas import ResultDraft, RuleIn, RuleResultOut

UNVERIFIED = "La IA no evaluó esta regla; se cuenta como no cumplida."
NO_QUOTE = "No se encontró en la entrega la cita que respalda esta regla; se cuenta como no cumplida."


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def verify_results(rules: list[RuleIn], drafts: list[ResultDraft], delivery_text: str) -> list[RuleResultOut]:
    delivery = squash(delivery_text)
    by_position: dict[int, ResultDraft] = {}
    for draft in drafts:
        by_position.setdefault(draft.position, draft)

    results: list[RuleResultOut] = []
    for rule in rules:
        draft = by_position.get(rule.position)
        if draft is None:
            results.append(RuleResultOut(position=rule.position, met=False, reasoning=UNVERIFIED, evidence_excerpt=None))
            continue

        excerpt = (draft.evidence_excerpt or "").strip()
        quoted = bool(excerpt) and squash(excerpt) in delivery
        reasoning = draft.reasoning.strip()[:1000] or "Sin explicación"
        if draft.met and not quoted:
            reasoning = f"{NO_QUOTE} ({reasoning[:300]})"
        results.append(
            RuleResultOut(
                position=rule.position,
                met=draft.met and quoted,
                reasoning=reasoning,
                evidence_excerpt=excerpt[:500] if quoted else None,
            )
        )
    return results
