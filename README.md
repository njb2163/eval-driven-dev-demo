# The Copper Spoon — eval-driven development demo

A minimal, runnable walkthrough of eval-driven development. A menu-blurb agent for
a bistro, scored across six dimensions, showing how a greedy prompt edit silently
regresses requirements you weren't looking at.

## Start here — the narrative

These two docs are the story this code tells. Read or skim them before diving into
the files:

- **[`demo/docs/scenario-brief.md`](demo/docs/scenario-brief.md)** — the client
  brief: who The Copper Spoon is, and what "good" means (the requirements).
- **[`demo/docs/walkthrough-script.md`](demo/docs/walkthrough-script.md)** — a
  step-by-step, narrated walkthrough of the code in the order to read (or present) it.

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

**4. Adapt to the new requirement — and prove the fix.**
```bash
python evals_v3.py
```
Update the ground truth (`dataset_v3.py`) and the prompt (`SYSTEM_PROMPT_V3`), then
score `V1 → V2 → V3` against the updated bar. V3 satisfies the allergen requirement
*and* recovers the dimensions V2 broke — with evals proving it, not guesswork.

## The files (in `demo/`)

| File | What it is |
|------|------------|
| `agent.py` | The system under test — one Anthropic call, a system prompt, no tools. `V1` + the greedy `V2` + the fixed `V3`. |
| `dataset.py` | The eval dataset + **ground-truth** golden references. |
| `scoring.py` | Six scorers — deterministic, LLM-judge, and ground-truth — all returning `(score, reason)`. |
| `greedy.py` | The no-evals workflow: generate and print, no measurement. |
| `evals.py` | The eval suite: score both prompt versions across all dimensions, print the V1→V2 scorecard. |
| `dataset_v3.py` | Updated ground truth after allergens became a requirement — the references `V3` targets. |
| `evals_v3.py` | The fix: score `V1 → V2 → V3` against the updated ground truth. |

## Dimensions

| Dimension | Technique |
|-----------|-----------|
| `length_ok` | deterministic (≤ 20 words) |
| `mentions_ingredients` | deterministic |
| `allergen_callout` | deterministic (the added requirement) |
| `appetizing` | LLM judge (reference-free) |
| `brand_voice` | LLM judge (reference-free) |
| `reference_match` | LLM judge vs. ground truth |
