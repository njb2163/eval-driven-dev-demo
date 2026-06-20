"""Eval-driven development: measure every dimension, every time.

Runs the whole dataset through BOTH prompt versions, scores all six dimensions,
and prints a scorecard with the V1 -> V2 delta per dimension.

    python evals.py

The reveal: the greedy allergen edit (V2) makes `allergen_callout` jump, but
`appetizing`, `length_ok`, and `reference_match` quietly drop. One requirement
satisfied, three regressed — invisible to the greedy workflow, obvious here.
That's thrashing, and evals across all dimensions are how you catch it.
"""

from agent import write_description
from dataset import MENU
from scoring import (
    score_allergen_callout,
    score_appetizing,
    score_brand_voice,
    score_length,
    score_mentions_ingredients,
    score_reference_match,
)

# (name, technique, scorer). Some scorers need the dish (for ground truth /
# expected ingredients), so every scorer is called as fn(description, dish).
SCORERS = [
    ("length_ok",            "deterministic", lambda d, dish: score_length(d)),
    ("mentions_ingredients", "deterministic", lambda d, dish: score_mentions_ingredients(d, dish)),
    ("allergen_callout",     "deterministic", lambda d, dish: score_allergen_callout(d, dish)),
    ("appetizing",           "LLM judge",     lambda d, dish: score_appetizing(d)),
    ("brand_voice",          "LLM judge",     lambda d, dish: score_brand_voice(d)),
    ("reference_match",      "ground truth",  lambda d, dish: score_reference_match(d, dish)),
]


def run_version(version: str) -> dict[str, float]:
    """Generate + score every dish; return the average score per dimension."""
    totals = {name: 0.0 for name, _, _ in SCORERS}
    for dish in MENU:
        description = write_description(dish, version)
        for name, _technique, scorer in SCORERS:
            totals[name] += scorer(description, dish).score
    return {name: totals[name] / len(MENU) for name in totals}


def main() -> None:
    print("\nRunning evals across all dimensions for both prompt versions...\n")
    v1 = run_version("v1")
    v2 = run_version("v2")  # v2 = greedy "add allergens" edit

    print("=" * 74)
    print(f"{'dimension':<22}{'technique':<16}{'V1':>7}{'V2':>9}{'change':>16}")
    print("-" * 74)
    for name, technique, _ in SCORERS:
        delta = v2[name] - v1[name]
        if delta > 0.02:
            arrow = f"  UP   +{delta:.2f}"
        elif delta < -0.02:
            arrow = f"  DOWN {delta:+.2f}"
        else:
            arrow = "  --"
        print(f"{name:<22}{technique:<16}{v1[name]:>7.2f}{v2[name]:>9.2f}{arrow:>16}")
    print("=" * 74)

    regressions = [n for n, _, _ in SCORERS if v2[n] - v1[n] < -0.02]
    print(
        "\nThe greedy edit satisfied the new allergen requirement — but "
        f"{len(regressions)} other dimension(s) silently regressed:"
        f"\n  {', '.join(regressions) or 'none'}"
    )
    print("Without evals across all dimensions, we'd have shipped V2 and never known.\n")


if __name__ == "__main__":
    main()
