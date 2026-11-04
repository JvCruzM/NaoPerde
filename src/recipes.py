
"""Modulo de sugestao e consulta de receitas do NaoPerde."""

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
    """Padroniza nomes para facilitar a comparacao."""

    name = str(name).strip().lower()

    name = unicodedata.normalize("NFD", name)

    name = "".join(
        char for char in name
        if unicodedata.category(char) != "Mn"
    )

    return name


def suggest_recipes(inventory, limit=5):
    """
    Compara os alimentos do estoque com as receitas.

    inventory: lista de produtos com o campo 'nome'.
    limit: quantidade maxima de receitas retornadas.
    """

    if limit < 1:
        raise ValueError("O limite deve ser maior que zero.")

    available = {
        normalize_name(item["nome"])
        for item in inventory
        if item.get("nome")
    }

    suggestions = []

    for recipe in RECIPES:

        ingredients = {
            normalize_name(item)
            for item in recipe["ingredients"]
        }

        matched = ingredients.intersection(available)
        missing = ingredients.difference(available)

        # Ignora receitas sem nenhum ingrediente disponivel.
        if not matched:
            continue

        percentage = (
            len(matched) / len(ingredients)
        ) * 100

        suggestions.append({
            "name": recipe["name"],
            "ingredients": recipe["ingredients"],
            "available_ingredients": sorted(matched),
            "missing_ingredients": sorted(missing),
            "match_percentage": round(percentage, 2),
            "instructions": recipe["instructions"]
        })

    # Prioriza receitas com menos ingredientes faltantes.
    suggestions.sort(
        key=lambda recipe: (
            len(recipe["missing_ingredients"]),
            -recipe["match_percentage"]
        )
    )

    return suggestions[:limit]


def get_recipe_details(recipe_name):
    """Busca os detalhes de uma receita pelo nome."""

    normalized_search = normalize_name(recipe_name)

    for recipe in RECIPES:

        if normalize_name(recipe["name"]) == normalized_search:
            return recipe.copy()

    return None
