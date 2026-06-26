"""Scoring functions — one per dimension.

Every scorer returns a ScoreResult: a float in [0, 1] plus a human-readable
reason. That uniform contract is what lets us treat very different techniques
(string checks vs. an LLM judging tone) as comparable numbers in the scorecard.

Three techniques are on display:
  - Deterministic  : pure code, no model. Cheap, fast, perfectly repeatable.
      score_length, score_mentions_ingredients, score_allergen_callout
  - LLM-as-judge   : ask a model to rate something a regex can't (reference-free).
      score_appetizing, score_brand_voice
  - Ground-truth   : an LLM judge that compares the output to the golden reference.
      score_reference_match
"""

from dataclasses import dataclass

from pydantic import BaseModel

from agent import MODEL, client


@dataclass
class ScoreResult:
    score: float  # 0.0 - 1.0
    reason: str


# --------------------------------------------------------------------------- #
# Deterministic scorers — just code. No model, no cost, fully repeatable.
# --------------------------------------------------------------------------- #

WORD_LIMIT = 20


def score_length(description: str) -> ScoreResult:
    """1.0 if within the word limit, degrading as it runs over."""
    words = len(description.split())
    if words <= WORD_LIMIT:
        return ScoreResult(1.0, f"{words} words (<= {WORD_LIMIT})")
    over = words - WORD_LIMIT
    score = max(0.0, 1.0 - over / WORD_LIMIT)
    return ScoreResult(score, f"{words} words ({over} over the {WORD_LIMIT} limit)")


def score_mentions_ingredients(description: str, dish) -> ScoreResult:
    """Fraction of the dish's key ingredients that show up in the blurb."""
    text = description.lower()
    hits = [ing for ing in dish.ingredients if _mentions(text, ing)]
    score = len(hits) / len(dish.ingredients)
    missing = [ing for ing in dish.ingredients if ing not in hits]
    reason = f"{len(hits)}/{len(dish.ingredients)} ingredients"
    if missing:
        reason += f" (missing: {', '.join(missing)})"
    return ScoreResult(score, reason)


def score_allergen_callout(description: str, dish) -> ScoreResult:
    """Fraction of the dish's allergens that are named. 1.0 if there are none."""
    if not dish.allergens:
        return ScoreResult(1.0, "no allergens to call out")
    text = description.lower()
    named = [a for a in dish.allergens if _mentions(text, a)]
    score = len(named) / len(dish.allergens)
    missing = [a for a in dish.allergens if a not in named]
    reason = f"{len(named)}/{len(dish.allergens)} allergens named"
    if missing:
        reason += f" (missing: {', '.join(missing)})"
    return ScoreResult(score, reason)


def _mentions(text: str, phrase: str) -> bool:
    """Loose match: the phrase, or any meaningful word in it, appears in text."""
    phrase = phrase.lower()
    if phrase in text:
        return True
    # e.g. "tree nuts" -> match on "nut"; "heirloom tomatoes" -> "tomato"
    return any(word[:-1] in text or word in text for word in phrase.split() if len(word) > 3)


# --------------------------------------------------------------------------- #
# LLM-as-judge — for things a regex can't measure (tone, craving, similarity).
# Each judge returns a 1-5 score; we normalize to [0, 1].
# --------------------------------------------------------------------------- #

class Judgement(BaseModel):
    score: int  # 1 (poor) .. 5 (excellent)
    reason: str


def _judge(system: str, content: str) -> ScoreResult:
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": content}],
        output_format=Judgement,
    )
    j = resp.parsed_output
    raw = max(1, min(5, j.score))  # clamp defensively
    return ScoreResult((raw - 1) / 4, f"{raw}/5 — {j.reason}")


def score_appetizing(description: str) -> ScoreResult:
    """Reference-free judge: does this blurb make you hungry?"""
    system = (
        "You rate menu descriptions on how appetizing they are, 1-5. "
        "5 = mouth-watering and sensory, you want to order it immediately. "
        "1 = flat, clinical, or off-putting. "
        "A brief, natural allergen note (e.g. 'Contains dairy.') is fine — do NOT "
        "penalize it. But a long or formal disclaimer, like an 'Allergen notice: "
        "...' sentence, reads like a warning label and kills the craving — rate "
        "those no higher than 2."
    )
    return _judge(system, f"Menu description: {description}")


def score_brand_voice(description: str) -> ScoreResult:
    """Reference-free judge: cozy, playful bistro voice — not corporate."""
    system = (
        "You rate menu descriptions on brand voice for a cozy neighborhood "
        "bistro, 1-5. 5 = warm, playful, inviting. 1 = corporate, clinical, or "
        "cold. A brief, natural allergen note (e.g. 'Contains dairy.') is fine. "
        "But a long or formal disclaimer, like an 'Allergen notice: ...' "
        "sentence, reads like legal boilerplate and breaks the cozy voice — rate "
        "those no higher than 2."
    )
    return _judge(system, f"Menu description: {description}")


def score_reference_match(description: str, dish) -> ScoreResult:
    """Ground-truth judge: how close is the output to the golden reference?"""
    system = (
        "You compare a generated menu description to a GOLDEN reference written "
        "by the client — the gold standard for this dish. Rate 1-5 how well the "
        "generated one matches the reference's quality, content, length, and "
        "style, including how it handles (or omits) an allergen note. 5 = as good "
        "as the reference and covers the same appeal. 1 = far off in tone, length, "
        "or content."
    )
    content = (
        f"Golden reference: {dish.reference}\n"
        f"Generated description: {description}"
    )
    return _judge(system, content)
