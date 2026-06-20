"""The eval dataset + ground truth.

Each dish carries:
  - name / ingredients : the agent's input
  - allergens          : ground truth for the deterministic allergen scorer
  - reference          : the GOLDEN blurb — what "good" looks like

The references are our ground truth for quality. In a real engagement you'd get
these from the client (ideal), approximate them from existing data, or synthesize
them and have a human approve (what we did here). Either way, anchoring on real
"good" examples keeps us honest instead of guessing at arbitrary requirements.

Notice every reference is short, sensory, and on-voice — and none of them recite
allergens. That's the latent conflict the greedy allergen edit will collide with.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Dish:
    name: str
    ingredients: list[str]
    allergens: list[str] = field(default_factory=list)
    reference: str = ""  # ground-truth "golden" description


MENU = [
    Dish(
        name="Burrata & Heirloom Tomato",
        ingredients=["burrata", "heirloom tomatoes", "basil", "olive oil"],
        allergens=["dairy"],
        reference="Silky burrata over sun-ripened heirloom tomatoes, torn basil, "
        "and a drizzle of grassy olive oil.",
    ),
    Dish(
        name="Walnut Pesto Tagliatelle",
        ingredients=["tagliatelle", "walnut pesto", "parmesan", "cream"],
        allergens=["tree nuts", "dairy", "gluten"],
        reference="Ribbons of tagliatelle tangled in toasted walnut pesto, "
        "finished with a whisper of parmesan.",
    ),
    Dish(
        name="Charred Corn Ribs",
        ingredients=["corn", "chili butter", "lime", "cotija"],
        allergens=["dairy"],
        reference="Smoky charred corn ribs slicked with chili-lime butter and a "
        "snowfall of crumbled cotija.",
    ),
    Dish(
        name="Garden Chickpea Salad",
        ingredients=["chickpeas", "cucumber", "mint", "lemon"],
        allergens=[],  # nothing to call out — a useful control case
        reference="Bright chickpeas tumbled with crisp cucumber, fresh mint, and a "
        "squeeze of sunny lemon.",
    ),
    Dish(
        name="Brown Butter Skillet Cookie",
        ingredients=["cookie dough", "brown butter", "dark chocolate", "sea salt"],
        allergens=["dairy", "gluten"],
        reference="A warm skillet cookie of nutty brown butter and molten dark "
        "chocolate, kissed with flaky sea salt.",
    ),
    Dish(
        name="Hazelnut Affogato",
        ingredients=["espresso", "vanilla gelato", "hazelnut"],
        allergens=["tree nuts", "dairy"],
        reference="Hot espresso poured over cold vanilla gelato, finished with "
        "toasted hazelnut crunch.",
    ),
]
