# Eval-Driven Development — demo

A minimal, runnable demo of **eval-driven development** for LLM systems: instead of
editing a prompt whenever a new problem appears and eyeballing a few outputs, you
score the system against a fixed set of requirements on every change.

The example is a menu-description writer for a fictional bistro, "The Copper Spoon."
It's scored across six dimensions using three techniques — deterministic checks,
LLM-as-judge, and ground-truth comparison. A single greedy prompt edit (adding an
allergen callout) then shows how fixing one requirement can silently regress
others — a regression only the eval suite reveals.

## Quick start

```bash
cd demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY

python greedy.py v1         # the naive workflow: generate, eyeball, "ship it"
python greedy.py v2         # after a greedy "add allergens" prompt edit
python evals.py             # the reveal: a V1 -> V2 scorecard across all dimensions
```

You'll need an Anthropic API key. The demo uses `claude-haiku-4-5` (cheap and fast).

## Files (in `demo/`)

| File | What it is |
|------|------------|
| `agent.py` | The system under test — one Anthropic call, a system prompt, no tools. `V1` + the greedy `V2`. |
| `dataset.py` | The eval dataset + ground-truth "golden" references. |
| `scoring.py` | Six scorers (deterministic, LLM-judge, ground-truth), all returning `(score, reason)`. |
| `greedy.py` | The no-evals workflow: generate and print, no measurement. |
| `evals.py` | The eval suite: score both prompt versions across all dimensions, print the scorecard. |

## Dimensions

| Dimension | Technique |
|-----------|-----------|
| `length_ok` | deterministic (≤ 20 words) |
| `mentions_ingredients` | deterministic |
| `allergen_callout` | deterministic (the added requirement) |
| `appetizing` | LLM judge (reference-free) |
| `brand_voice` | LLM judge (reference-free) |
| `reference_match` | LLM judge vs. ground truth |
