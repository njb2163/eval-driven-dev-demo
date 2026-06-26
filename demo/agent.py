"""The system under test: a menu-description writer for The Copper Spoon.

Deliberately minimal — one Anthropic chat call, a system prompt, no tools. We use
a cheap, fast model (Haiku) on purpose: it's quick to run live and easy enough to
break that the regression in the talk actually shows up.

There are three system prompts:
  V1 — the original four requirements.
  V2 — V1 plus the greedy allergen edit (a clinical "Allergen notice:" line).
  V3 — V1 plus a graceful allergen note; the fix the evals point you toward.
Everything else is identical, so any score change between versions is caused by
that one added rule.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

# override=True so the project's .env wins over any ANTHROPIC_API_KEY already
# exported in your shell (e.g. Claude Code's credential), which otherwise takes
# precedence and causes a 401.
load_dotenv(override=True)

# Cheap + fast + easy to break, so the regression is visible in a live demo.
MODEL = "claude-haiku-4-5"

# One shared client; reused by the judges in scoring.py too.
client = Anthropic()


SYSTEM_PROMPT_V1 = """\
You write menu item descriptions for The Copper Spoon, a cozy neighborhood bistro.

Follow every rule:
- Keep it under 20 words.
- Mention the dish's key ingredients.
- Make it mouth-watering and sensory.
- Use a warm, cozy, playful tone — never corporate or clinical.

Return ONLY the description text. No preamble, no quotes, no "Here is...".\
"""

# The greedy edit: the client asked for allergen callouts, so we bolt one rule on.
# This is the ONLY difference between V1 and V2. We demand a clinical notice line
# (what a cautious restaurant would actually do) — which is exactly what collides
# with "short" and "mouth-watering".
ALLERGEN_RULE = (
    "\n- IMPORTANT: at the very end, append an allergen notice in exactly this "
    "format: 'Allergen notice: contains <comma-separated allergens>.'"
)

SYSTEM_PROMPT_V2 = SYSTEM_PROMPT_V1 + ALLERGEN_RULE

# V3 — the iterated fix. Same allergen requirement, satisfied with a brief, natural
# note instead of a clinical disclaimer, so the blurb stays short, appetizing, and
# on-brand. This is what "adapting to a new requirement" looks like once you let the
# evals guide the next prompt edit (see dataset_v3.py + evals_v3.py).
ALLERGEN_RULE_V3 = (
    "\n- If the dish contains nuts, dairy, or gluten, end with a brief, natural "
    "allergen note such as 'Contains dairy.' or 'Contains nuts, dairy.' Keep it "
    "short and keep the whole blurb appetizing and on-brand — never a long or "
    "clinical disclaimer. Stay within the 20-word limit including the note."
)

SYSTEM_PROMPT_V3 = SYSTEM_PROMPT_V1 + ALLERGEN_RULE_V3

PROMPTS = {"v1": SYSTEM_PROMPT_V1, "v2": SYSTEM_PROMPT_V2, "v3": SYSTEM_PROMPT_V3}


def write_description(dish, version: str = "v1") -> str:
    """Run the agent on one dish and return its menu blurb."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=PROMPTS[version],
        messages=[
            {
                "role": "user",
                "content": f"Dish: {dish.name}\nIngredients: {', '.join(dish.ingredients)}",
            }
        ],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()
