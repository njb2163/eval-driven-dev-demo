"""The greedy workflow: run the agent, read a few outputs, ship it.

This is what "developing by prompt-patching" looks like — no measurement, just
eyeballing. Run it on v1, then (after the client's allergen request) on v2:

    python greedy.py v1
    python greedy.py v2

Both runs look fine to the naked eye. v2's blurbs even list allergens like the
client asked. Nothing here tells you that v2 quietly got less appetizing, longer,
and further from what "good" looks like. That's the trap — see evals.py.
"""

import sys

from agent import write_description
from dataset import MENU


def main(version: str) -> None:
    print(f"\n=== The Copper Spoon — menu blurbs (prompt {version.upper()}) ===\n")
    for dish in MENU:
        description = write_description(dish, version)
        print(f"  {dish.name}")
        print(f"    {description}\n")
    print("Looks good. Ship it? (This is the greedy approach — we never measured.)\n")


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    if version not in ("v1", "v2", "v3"):
        sys.exit("usage: python greedy.py [v1|v2|v3]")
    main(version)
