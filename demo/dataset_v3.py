"""Updated ground truth — after allergens became a requirement.

Same dishes as dataset.py, but the golden references now model the GOOD way to
satisfy the new requirement: a short, natural allergen note that keeps the blurb
appetizing and on-brand. When a requirement changes, the ground truth has to
change with it — otherwise the eval grades against a stale definition of "good."

This is the reference set the V3 prompt is built to match. Compare a `reference`
here with the same dish in dataset.py to see exactly what changed.
"""

from dataset import Dish

MENU = [
    Dish(
        name="Burrata & Heirloom Tomato",
        ingredients=["burrata", "heirloom tomatoes", "basil", "olive oil"],
        allergens=["dairy"],
        reference="Silky burrata over sun-ripened heirloom tomatoes, torn basil, "
        "and grassy olive oil. Contains dairy.",
    ),
    Dish(
        name="Walnut Pesto Tagliatelle",
        ingredients=["tagliatelle", "walnut pesto", "parmesan", "cream"],
        allergens=["tree nuts", "dairy", "gluten"],
        reference="Ribbons of tagliatelle in toasted walnut pesto with a whisper "
        "of parmesan. Contains nuts, dairy, gluten.",
    ),
    Dish(
        name="Charred Corn Ribs",
        ingredients=["corn", "chili butter", "lime", "cotija"],
        allergens=["dairy"],
        reference="Smoky charred corn ribs slicked with chili-lime butter and "
        "crumbled cotija. Contains dairy.",
    ),
    Dish(
        name="Garden Chickpea Salad",
        ingredients=["chickpeas", "cucumber", "mint", "lemon"],
        allergens=[],  # nothing to call out — the note should be omitted here
        reference="Bright chickpeas tumbled with crisp cucumber, fresh mint, and a "
        "squeeze of sunny lemon.",
    ),
    Dish(
        name="Brown Butter Skillet Cookie",
        ingredients=["cookie dough", "brown butter", "dark chocolate", "sea salt"],
        allergens=["dairy", "gluten"],
        reference="A warm skillet cookie of nutty brown butter and molten dark "
        "chocolate, flaky sea salt. Contains dairy, gluten.",
    ),
    Dish(
        name="Hazelnut Affogato",
        ingredients=["espresso", "vanilla gelato", "hazelnut"],
        allergens=["tree nuts", "dairy"],
        reference="Hot espresso poured over cold vanilla gelato with toasted "
        "hazelnut crunch. Contains nuts, dairy.",
    ),
]
