from datetime import date
import json
import pytest
from src import inventory


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "DATA_FILE", tmp_path / "data" / "inventory.json")
    return inventory.DATA_FILE


def test_load_legacy_format(storage):
    storage.parent.mkdir(parents=True)
    storage.write_text(json.dumps({"alimentos": []}), encoding="utf-8")
    assert inventory.load_inventory() == []


def test_add_food_persists_canonical_list(storage):
    food = inventory.add_food("Tomate", 2, "unidades", date(2026, 11, 10), "Hortifruti")
    assert food["name"] == "Tomate"
    assert inventory.load_inventory()[0]["id"] == food["id"]
    assert isinstance(json.loads(storage.read_text()), list)


def test_update_food_accepts_iso_date(storage):
    food = inventory.add_food("Leite", 1, "litro", "2026-11-10", "Laticinios")
    updated = inventory.update_food(food["id"], expiration_date="2026-11-12", quantity=2)
    assert updated["expiration_date"] == "2026-11-12"
    assert updated["quantity"] == 2


@pytest.mark.parametrize("quantity", [0, -1, "abc", float("inf"), True])
def test_rejects_invalid_quantity(storage, quantity):
    with pytest.raises(ValueError):
        inventory.add_food("Arroz", quantity, "kg", "2026-11-10", "Graos")


def test_status_and_remove(storage):
    food = inventory.add_food("Queijo", 200, "g", "2026-11-10", "Laticinios")
    assert inventory.mark_as_consumed(food["id"]) is True
    assert inventory.get_inventory(only_available=True) == []
    assert inventory.remove_food(food["id"]) is True
    assert inventory.remove_food(food["id"]) is False


def test_corrupt_json_does_not_get_overwritten(storage):
    storage.parent.mkdir(parents=True)
    storage.write_text("{invalido", encoding="utf-8")
    with pytest.raises(ValueError, match="corrompido"):
        inventory.load_inventory()
    assert storage.read_text(encoding="utf-8") == "{invalido"
