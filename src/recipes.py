
import unicodedata


RECIPES = [
    {
        "name": "Omelete de tomate e queijo",
        "ingredients": ["ovo", "tomate", "queijo"],
        "instructions": [
            "Bata os ovos em um recipiente.",
            "Corte o tomate em pequenos pedacos.",
            "Adicione o tomate e o queijo aos ovos.",
            "Cozinhe em uma frigideira ate ficar completamente pronto."
        ]
    },
    {
        "name": "Panqueca simples",
        "ingredients": ["ovo", "leite", "farinha"],
        "instructions": [
            "Misture o ovo, o leite e a farinha.",
            "Mexa ate obter uma massa homogenea.",
            "Coloque pequenas porcoes em uma frigideira.",
            "Doure os dois lados."
        ]
    },
    {
        "name": "Macarrao com queijo e tomate",
        "ingredients": ["macarrao", "queijo", "tomate"],
        "instructions": [
            "Cozinhe o macarrao conforme as instrucoes da embalagem.",
            "Pique o tomate.",
            "Prepare o acompanhamento com tomate e queijo.",
            "Misture ao macarrao."
        ]
    },
    {
        "name": "Omelete simples",
        "ingredients": ["ovo", "queijo"],
        "instructions": [
            "Bata os ovos.",
            "Adicione o queijo.",
            "Coloque em uma frigideira.",
            "Cozinhe completamente."
        ]
    }
]


def normalize_name(name):

    name = str(name).strip().lower()

    name = unicodedata.normalize("NFD", name)

    name = "".join(
        char for char in name
        if unicodedata.category(char) != "Mn"
    )

    return name


def compare_ingredients(required, inventory):

    available = {
        normalize_name(food["name"])
        for food in inventory
        if food.get("name")
        and food.get("status") == "disponivel"
    }

    found = []
    missing = []

    for ingredient in required:

        if normalize_name(ingredient) in available:
            found.append(ingredient)
        else:
            missing.append(ingredient)

    return {
        "available": found,
        "missing": missing
    }


def suggest_recipes(inventory, limit=5):

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("O limite deve ser um numero inteiro maior que zero.")

    if not isinstance(inventory, (list, tuple)):
        raise ValueError("O estoque deve ser uma lista de produtos.")

    available = {
        normalize_name(item["name"])
        for item in inventory
        if item.get("name")
        and item.get("status") == "disponivel"
    }

    suggestions = []

    for recipe in RECIPES:

        ingredients = recipe["ingredients"]

        matched = [
            ingredient
            for ingredient in ingredients
            if normalize_name(ingredient) in available
        ]

        missing = [
            ingredient
            for ingredient in ingredients
            if normalize_name(ingredient) not in available
        ]

        if not matched:
            continue

        percentage = (
            len(matched) / len(ingredients)
        ) * 100

        suggestions.append({
            "name": recipe["name"],
            "ingredients": ingredients.copy(),
            "available_ingredients": matched,
            "missing_ingredients": missing,
            "match_percentage": round(percentage, 2),
            "instructions": recipe["instructions"].copy()
        })

    suggestions.sort(
        key=lambda recipe: (
            -recipe["match_percentage"],
            len(recipe["missing_ingredients"])
        )
    )

    return suggestions[:limit]


def get_recipe_details(recipe_name):

    normalized_search = normalize_name(recipe_name)

    for recipe in RECIPES:

        if normalize_name(recipe["name"]) == normalized_search:

            return {
                "name": recipe["name"],
                "ingredients": recipe["ingredients"].copy(),
                "instructions": recipe["instructions"].copy()
            }

    return None
