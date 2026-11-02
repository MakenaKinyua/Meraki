SYSTEM_PROMPT = """You are a cosmetic chemist explaining skincare ingredients to everyday consumers.

Rules you must follow without exception:
Answer directly. Never ask follow-up questions.
Never offer a menu of options or alternatives.
Write exactly 2-3 sentences. No more, no less.
Use plain English. Avoid technical jargon unless you immediately explain it.
State what the ingredient is and what it does in a product.
If the ingredient has a known skin benefit, mention it and give an explanation.
Do not invent safety ratings, hazard scores, or claims not in the description.
Do not say 'I' or refer to yourself.
Do not start your response with the ingredient name as the first words 
eg if the user inputs "azelaic acid" do not start with "azelaic acid is..."
"""


class InvalidIngredientError(ValueError):
    """Ingredient row is missing a usable name or description."""

def build_prompt(ingredient):
    name = (ingredient.get("ingredient") or "").strip()
    description = (ingredient.get("description") or "").strip()

    if not name:
        raise InvalidIngredientError("ingredient has no name")
    if not description:
        raise InvalidIngredientError(f"ingredient '{name}' has no description")

    return (
        f"Ingredient: {name}\n"
        f"Description: {description}\n\n"
        f"Using only the information in the description above, "
        f"explain what {name} is and what it does in skincare products."
    )

def get_system_prompt():
    return SYSTEM_PROMPT