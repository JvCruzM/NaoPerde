import pytest
from src.recipes import compare_ingredients, get_recipe_details, normalize_name, suggest_recipes


def test_normalize_accents_and_case():
    assert normalize_name("  Hortifrúti ") == "hortifruti"


def test_compare_only_available_items():
    stock = [
        {"name": "Tomaté", "status": "disponivel"},
        {"name": "Queijo", "status": "consumido"}
    ]
    result = compare_ingredients(["tomate", "queijo"], stock)
    assert result == {"available": ["tomate"], "missing": ["queijo"]}


def test_recipe_suggestions_rank_by_match():
    stock = [
        {"name": "ovo", "status": "disponivel"},
        {"name": "queijo", "status": "disponivel"}
    ]
    results = suggest_recipes(stock)
    assert results[0]["name"] == "Omelete simples"
    assert results[0]["match_percentage"] == 100
    assert results[0]["quantity_checked"] is False


def test_recipe_details_is_copy():
    recipe = get_recipe_details("OMELETE SIMPLES")
    assert recipe is not None
    recipe["ingredients"].append("intruso")
    assert "intruso" not in get_recipe_details("omelete simples")["ingredients"]


def test_invalid_input():
    with pytest.raises(ValueError):
        suggest_recipes([], limit=0)
    with pytest.raises(ValueError):
        compare_ingredients("ovo", [])
