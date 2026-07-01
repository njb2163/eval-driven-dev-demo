# Live code walkthrough — presenter script

A spoken script for walking the audience through the code instead of the slides.
It follows the same narrative as `slides/Eval Driven Development.pdf`. Each beat has
**Say** (talking points, not a script to read word-for-word), **Do** (what to open
or run), and **Point out** (what to highlight on screen).

> **Before you start:** open a terminal in `demo/` with the venv active and
> `ANTHROPIC_API_KEY` set; bump your editor + terminal font size. Have these files
> ready to open: `scenario-brief.md`, `demo/agent.py`, `demo/dataset.py`,
> `demo/dataset_v3.py`, `demo/scoring.py`. Total run time ~12–15 min.

---

## 1. The scenario  ·  (slides 1–2)

**Do:** Open `scenario-brief.md` (Markdown preview).

**Say:**
- We're building an agent for The Copper Spoon, a small bistro. It writes the
  descriptions for items on their menu.
- Give it a dish and its ingredients, it writes a short, mouth-watering blurb.
- The thing to notice: there's no single right answer. "Accurate" isn't enough —
  a good blurb has to be short, accurate, appetizing, and on-brand, all at once.
- And the owner gave us "golden" examples of blurbs they love. Hold onto that —
  it matters later.

---

## 2. Where do we start?  ·  (slides 3–4)

**Say:**
- The naive approach: build an agent with a system prompt that lists these
  requirements, test it on a few inputs, and ship it.
- This works in the short term — but it struggles to scale. Let me show you why.

**Do:** Open `demo/agent.py`. Walk through `SYSTEM_PROMPT_V1`.

**Point out:**
- It's just a system prompt — the four requirements written out in English. No
  tools, one model call. (Note the cheap model, `claude-haiku-4-5` — fast, and
  weak enough that problems show up clearly.)

**Do:** Run the naive version:
```bash
python greedy.py v1
```

**Point out:**
- Read two or three blurbs aloud. They're short, they name the ingredients, they
  sound good. By eye, this looks done.
- This is how most prompt work happens: write the prompt, glance at a few outputs,
  ship. "Looks right to me" is the only test.

---

## 3. A new requirement → where it falls short  ·  (slide 5)

**Say:**
- Two weeks in, the client comes back: "We're getting allergy complaints. Every
  description has to call out allergens — nuts, dairy, gluten."
- The greedy fix is obvious: add a line to the prompt.

**Do:** In `demo/agent.py`, show `SYSTEM_PROMPT_V2` — point at the one added line
(`ALLERGEN_RULE`). It's the only difference from V1.

**Do:** Run it:
```bash
python greedy.py v2
```

**Point out:**
- The allergens are listed now. Requirement satisfied. By eye, still looks fine —
  so we'd ship it.
- But here's the problem: I only looked at the thing I just changed. I have no
  idea what this did to *short*, *appetizing*, or *on-brand*. With a handful of
  eyeballed outputs, I can't see it — and I can't see it scaling to hundreds of
  dishes either.

> **Remember to say:** Maybe *you* can hold every requirement in your head and keep
> scaling the prompt by hand as new ones come in. But what happens when another
> engineer onboards? How do they know a change they make doesn't quietly regress
> something you set up months ago? That's where evals earn their keep — they
> encode the requirements so anyone can change the prompt and immediately see what
> it cost.

---

## 4. What are evals  ·  (slide 6)

**Say:**
- The fix is to stop eyeballing and start measuring — on every requirement, every
  time we change something.
- An eval is three things: a fixed **dataset** of inputs, a **scorer** for each
  requirement, and a **runner** that scores everything on every change.
- It turns "looks good" into numbers you can compare between versions. It's
  regression testing for a system that doesn't have a single right answer.

---

## 5. Dataset + ground truth  ·  (slide 7)

**Do:** Open `demo/dataset.py`.

**Point out:**
- Each dish has its name and ingredients (the input), the allergens it contains
  (so we can check the callout), and a `reference` — the **golden** blurb.
- That golden blurb is our **ground truth**: what "great" actually looks like,
  approved by the client. We score against their taste, not our guesses.
- Where ground truth comes from, best to worst: get it from the client, approximate
  it from data you already have, or synthesize it and have a human approve.

---

## 6. Run the evals — the reveal  ·  (slide 8)

**Do:** Run the full suite (kick it off, then keep talking while it runs — it makes
a few dozen model calls):
```bash
python evals.py
```

**Say (while it runs):**
- This scores both prompt versions — V1 and the greedy V2 — across all six
  dimensions, and prints the change.

**Point out (on the scorecard):**
- `allergen_callout` jumped up — the new requirement is satisfied. ✅
- But `appetizing`, `brand_voice`, and `length_ok` all dropped — the clinical
  allergen line made the blurbs read like warning labels and pushed them over the
  word limit.
- And `reference_match` — the ground-truth score — dropped the most. The output
  drifted away from what the client actually wanted.
- This is the whole point: we fixed one requirement and silently broke four. The
  greedy workflow shipped this blind. Evals are the only reason we can see it.

---

## 7. How the scoring works  ·  (slides 9–11)

**Do:** Open `demo/scoring.py`.

### The contract (slide 9)
**Point out:**
- Every scorer returns the same thing: a number from 0 to 1, plus a reason.
- That sameness is what lets a word count and "does this make you hungry" live in
  one scorecard. One scorer per requirement — add a requirement, add a scorer.

### Deterministic scoring (slide 10)
**Point out:** `score_length`, `score_mentions_ingredients`, `score_allergen_callout`.
**Say:**
- These are just code — no model. Count the words, check the ingredients are named,
  check the allergens are listed. Cheap, instant, perfectly repeatable, free.
- Use these whenever the requirement is something you can check mechanically.

### LLM as judge (slide 11)
**Point out:** `score_appetizing`, `score_brand_voice`, `score_reference_match`.
**Say:**
- Some requirements code can't check — "is this appetizing," "is this on-brand."
  So we ask a model to grade them: a short rubric, a 1–5 score, normalized to 0–1.
- Two flavors: **reference-free** (judge the text on its own) and **reference-based**
  (`score_reference_match` compares against the golden blurb). Giving the judge a
  reference makes it much more reliable.
- One honest note: I had to *calibrate* these rubrics — early on the judge was too
  lenient to notice the regression. That's a real part of the work, which leads to…

---

## 8. Adapting to the new requirement — the fix (V3)  ·  (live, beyond the slides)

**Say:**
- Evals don't just catch the regression — they tell us how to fix it. We know V2
  satisfied allergens but tanked appetizing, brand voice, and length. So we make
  two moves: update the ground truth (the requirement changed), and write a better
  prompt — then let the evals confirm it actually worked.

**Do:** Open `demo/dataset_v3.py`.

**Point out:**
- Same dishes, but the golden references now model the *good* way to handle
  allergens — a short, natural note like "Contains dairy." inside an otherwise
  appetizing blurb. When the requirement changed, the ground truth changed with it.

**Do:** Open `demo/agent.py` and show `SYSTEM_PROMPT_V3`.

**Point out:**
- Same base as V1. Instead of V2's clinical "Allergen notice:" line, V3 asks for a
  brief, natural note that stays short and appetizing. One rule, rewritten.

**Do (optional):** eyeball it:
```bash
python greedy.py v3
```
- Allergens are there, but the blurbs still read like food, not a warning label.

**Do:** Run the three-way eval (kick it off, narrate while it runs):
```bash
python evals_v3.py
```

**Point out (on the scorecard):**
- It scores V1, V2, and V3 against the *updated* ground truth.
- `allergen_callout` climbs V1 → V2 → V3 — the new requirement gets satisfied.
- `appetizing` and `brand_voice` crash on V2 and come right back to full on V3.
- Overall, V3 is best on every dimension. The regression is gone.
- The point: we didn't guess our way here. Each prompt edit was a measurable step,
  and the evals told us when we'd actually fixed it — without quietly breaking
  something else. That's the loop. (`reference_match` is noisy and stays flattish —
  don't over-index on that one line; the judges and the allergen score carry it.)

---

## 9. Where to be careful  ·  (slide 12)

**Say (no code — just talk over the slide's points):**
- Judges are biased and noisy — they favor longer answers and wobble run to run.
  Calibrate against human-labeled examples and pin the model + prompt.
- They cost real money and time — prefer deterministic scorers where you can.
- You can game the metric — optimize hard enough and you satisfy the score, not the
  intent.
- **Ground truth has to track your requirements** — when the client added allergens,
  our golden references didn't include them, so part of that `reference_match` drop
  is stale ground truth. New requirement → update the references in the same change.
- Refresh the dataset over time, and never grade the model with itself —
  synthesized ground truth needs a human gate.

---

## 10. Eval platforms  ·  (slide 13)

**Say:**
- What we just ran is a real eval harness — it's a print loop, but it's the whole
  idea. You graduate to a platform when you want history, regression tracking over
  time, dataset management, and team sharing.
- Options: Braintrust, Weights & Biases (Weave), Langfuse, Promptfoo. The tool
  matters less than the discipline: a fixed dataset, a scorer per requirement, run
  on every change.

---

## 11. Close  ·  (slide 14)

**Say:**
- The greedy approach isn't lazy — it's the natural default, and it works right up
  until you have more than one requirement. Then fixing one thing quietly breaks
  another and you never find out.
- Evals make every dimension visible on every change. That's eval-driven
  development.

---

### Quick command reference
```bash
cd demo
python greedy.py v1     # naive approach, original prompt
python greedy.py v2     # naive approach, after the greedy allergen edit
python greedy.py v3     # the graceful fix
python evals.py         # V1 -> V2 scorecard — the regression
python evals_v3.py      # V1 -> V2 -> V3 vs updated ground truth — the fix
```

### Live-demo tips
- `evals.py` takes a bit (a few dozen API calls). Start it, then narrate while it
  runs — or run it once just before you present so the result is fresh in your
  scrollback as a fallback. `evals_v3.py` scores three versions, so it runs ~50%
  longer — same approach.
- If a judge score looks different from the deck's numbers, that's expected — it's a
  live model. The *direction* of the changes is the point, not the exact decimals.
- Keep `greedy.py v1` and `v2` outputs on screen side by side if you can — the v2
  allergen line is the visible "smoking gun" before you even run the evals.
