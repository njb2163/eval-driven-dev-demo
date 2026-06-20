# The Copper Spoon — eval-driven development demo

A minimal, runnable walkthrough of eval-driven development. A menu-blurb agent for
a bistro, scored across six dimensions, showing how a greedy prompt edit silently
regresses requirements you weren't looking at.

See the top-level `README.md` for an overview.

## Setup

```bash
cd demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your real ANTHROPIC_API_KEY in .env
```

Model: `claude-haiku-4-5` (cheap, fast, easy to break — chosen on purpose).

## The walkthrough

**1. The greedy approach — eyeball the output, ship it.**
```bash
python greedy.py v1
```
Nice blurbs. Looks done.

**2. The client adds a requirement:** *"call out allergens (nuts, dairy, gluten)."*
We greedily bolt one line onto the system prompt — that's `SYSTEM_PROMPT_V2` in
`agent.py` (the only difference from V1). Re-run and eyeball:
```bash
python greedy.py v2
```
Allergens are listed now. Greedy workflow says: ship it. ✅

**3. Run the evals — measure every dimension at once.**
```bash
python evals.py
```
The scorecard shows the truth: `allergen_callout` went up, but `appetizing`,
`length_ok`, and `reference_match` quietly went **down**. We fixed one thing and
broke three. That silent regression — invisible to step 2 — is what evals catch.

## The files

| File | What it is |
|------|------------|
| `agent.py` | The system under test — one Anthropic call, a system prompt, no tools. `V1` + the greedy `V2`. |
| `dataset.py` | The eval dataset + **ground-truth** golden references. |
| `scoring.py` | Six scorers — deterministic, LLM-judge, and ground-truth — all returning `(score, reason)`. |
| `greedy.py` | The no-evals workflow: generate and print, no measurement. |
| `evals.py` | The eval suite: score both prompt versions across all dimensions, print the V1→V2 scorecard. |

## Dimensions

| Dimension | Technique |
|-----------|-----------|
| `length_ok` | deterministic (≤ 20 words) |
| `mentions_ingredients` | deterministic |
| `allergen_callout` | deterministic (the new requirement) |
| `appetizing` | LLM judge (reference-free) |
| `brand_voice` | LLM judge (reference-free) |
| `reference_match` | LLM judge vs. ground truth |
