"""Iterating to a fix: V1 -> V2 -> V3 against UPDATED ground truth.

Once the client makes allergens a real requirement, the ground truth changes too:
`dataset_v3` has golden references that now include a brief, natural allergen note.
This scores all three prompt versions against that updated bar, so you can watch
the prompt iterations converge:

  V1  original (no allergens)              -> fails the new requirement
  V2  greedy clinical "Allergen notice:"   -> satisfies it, wrecks everything else
  V3  brief, natural allergen note         -> satisfies it AND recovers quality

Run:  python evals_v3.py
"""

from agent import write_description
from dataset_v3 import MENU
from scoring import (
    score_allergen_callout,
    score_appetizing,
    score_brand_voice,
    score_length,
    score_mentions_ingredients,
    score_reference_match,
)

SCORERS = [
    ("length_ok",            "deterministic", lambda d, dish: score_length(d)),
    ("mentions_ingredients", "deterministic", lambda d, dish: score_mentions_ingredients(d, dish)),
    ("allergen_callout",     "deterministic", lambda d, dish: score_allergen_callout(d, dish)),
    ("appetizing",           "LLM judge",     lambda d, dish: score_appetizing(d)),
    ("brand_voice",          "LLM judge",     lambda d, dish: score_brand_voice(d)),
    ("reference_match",      "ground truth",  lambda d, dish: score_reference_match(d, dish)),
]
VERSIONS = ["v1", "v2", "v3"]


def run_version(version: str) -> dict[str, float]:
    """Generate + score every dish for one prompt version; return per-dimension averages."""
    totals = {name: 0.0 for name, _, _ in SCORERS}
    for dish in MENU:
        description = write_description(dish, version)
        for name, _technique, scorer in SCORERS:
            totals[name] += scorer(description, dish).score
    return {name: totals[name] / len(MENU) for name in totals}


def main() -> None:
    print("\nScoring V1 -> V2 -> V3 against the UPDATED ground truth (allergens required)...\n")
    res = {v: run_version(v) for v in VERSIONS}

    print("=" * 72)
    print(f"{'dimension':<22}{'technique':<15}{'V1':>7}{'V2':>8}{'V3':>8}")
    print("-" * 72)
    for name, technique, _ in SCORERS:
        print(f"{name:<22}{technique:<15}{res['v1'][name]:>7.2f}{res['v2'][name]:>8.2f}{res['v3'][name]:>8.2f}")
    print("=" * 72)

    avg = {v: sum(res[v].values()) / len(SCORERS) for v in VERSIONS}
    print(f"\noverall mean   V1 {avg['v1']:.2f}   |   V2 {avg['v2']:.2f}   |   V3 {avg['v3']:.2f}")
    print(
        "\nV3 satisfies the new allergen requirement AND keeps the blurbs short,\n"
        "appetizing, on-brand, and close to the updated golden references. The\n"
        "regression V2 introduced is gone — and the evals are what let us iterate\n"
        "toward the fix instead of guessing.\n"
    )


if __name__ == "__main__":
    main()
