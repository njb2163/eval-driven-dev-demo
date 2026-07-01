# The Copper Spoon — project brief

**The client.** The Copper Spoon is a cozy neighborhood bistro. They've hired us
to build an agent that writes the descriptions for items on their menu.

**The task.** Give the agent a dish name and its ingredients; it returns a short,
mouth-watering blurb that fits on a menu.

> **Input:** Burrata & Heirloom Tomato — burrata, heirloom tomatoes, basil, olive oil
>
> **Output:** "Silky burrata over sun-ripened heirloom tomatoes, torn basil, and a
> drizzle of grassy olive oil."

**What "good" means.** There's no single correct answer, so "accuracy" alone isn't
enough. The owner gave us four requirements, and a good blurb has to hit all of
them at once:

1. **Short** — it has to fit on the menu (about 20 words or fewer).
2. **Accurate** — it names the dish's real ingredients, no invented food.
3. **Appetizing** — it should make you hungry.
4. **On-brand** — warm, cozy, and playful; never corporate.

**Ground truth.** For each dish, the owner also wrote a "golden" description — the
blurb they'd be happy to print. We keep these as our reference for what great looks
like, so we're measuring against the client's real taste, not our own guesses.

**The twist (coming up).** A couple of weeks in, the client adds a new requirement:
every description must call out common allergens — nuts, dairy, gluten. Simple
enough to satisfy. The interesting part is what it quietly does to everything else.
