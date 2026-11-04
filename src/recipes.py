
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
    if not isinstance(name, str) or not name.strip():
        raise ValueError("O nome do ingrediente deve ser um texto nao vazio.")
    normalized = unicodedata.normalize("NFD", name.strip().casefold())
    return "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def _available_names(inventory):
    if not isinstance(inventory, (list, tuple)):
        raise ValueError("O estoque deve ser uma lista de produtos.")
    available = set()
    for item in inventory:
        if not isinstance(item, dict):
            raise ValueError("O estoque contem um alimento invalido.")
        if item.get("status") == "disponivel" and item.get("name"):
            available.add(normalize_name(item["name"]))
    return available


def compare_ingredients(required, inventory):
    if not isinstance(required, (list, tuple)):
        raise ValueError("Os ingredientes necessarios devem estar em uma lista.")
    available_names = _available_names(inventory)
    found, missing = [], []
    for ingredient in required:
        normalized = normalize_name(ingredient)
        (found if normalized in available_names else missing).append(ingredient)
    return {"available": found, "missing": missing}


def suggest_recipes(inventory, limit=5):
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("O limite deve ser um numero inteiro maior que zero.")
    available = _available_names(inventory)
    suggestions = []
    for recipe in RECIPES:
        ingredients = recipe["ingredients"]
        matched = [item for item in ingredients if normalize_name(item) in available]
        missing = [item for item in ingredients if normalize_name(item) not in available]
        if not matched:
            continue
        suggestions.append({
            "name": recipe["name"],
            "ingredients": ingredients.copy(),
            "available_ingredients": matched,
            "missing_ingredients": missing,
            "match_percentage": round(len(matched) / len(ingredients) * 100, 2),
            "instructions": recipe["instructions"].copy(),
            "quantity_checked": False
        })
    suggestions.sort(key=lambda item: (-item["match_percentage"], len(item["missing_ingredients"])))
    return suggestions[:limit]


def get_recipe_details(recipe_name):
    normalized = normalize_name(recipe_name)
    for recipe in RECIPES:
        if normalize_name(recipe["name"]) == normalized:
            return {
                "name": recipe["name"],
                "ingredients": recipe["ingredients"].copy(),
                "instructions": recipe["instructions"].copy()
            }
    return None
