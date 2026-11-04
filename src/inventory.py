
import json
import math
import uuid
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "inventory.json"

VALID_STATUSES = {"disponivel", "consumido", "descartado"}
ALLOWED_FOOD_FIELDS = {
    "id", "name", "quantity", "unit", "expiration_date",
    "category", "status", "created_at"
}


def init_storage():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_inventory([])


def load_inventory():
    init_storage()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "O arquivo de estoque esta corrompido. Os dados nao foram alterados."
        ) from exc

    if isinstance(data, list):
        inventory = data
    elif isinstance(data, dict) and isinstance(data.get("alimentos"), list):
        inventory = data["alimentos"]
    else:
        raise ValueError(
            "Formato invalido do estoque. Esperada uma lista ou um objeto contendo 'alimentos'."
        )

    if any(not isinstance(item, dict) for item in inventory):
        raise ValueError("O estoque contem um registro de alimento invalido.")
    return inventory


def save_inventory(inventory):
    if not isinstance(inventory, list) or any(
        not isinstance(item, dict) for item in inventory
    ):
        raise ValueError("O estoque deve ser uma lista de alimentos.")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_suffix(".tmp")
    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(inventory, file, ensure_ascii=False, indent=4)
        temporary_file.replace(DATA_FILE)
    except Exception:
        if temporary_file.exists():
            temporary_file.unlink()
        raise


def normalize_expiration_date(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip()).isoformat()
        except ValueError as exc:
            raise ValueError(
                "Data invalida. Utilize o formato YYYY-MM-DD."
            ) from exc
    raise ValueError("Formato de data nao suportado.")


def validate_food(name, quantity, unit, expiration_date, category):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Informe um nome valido para o alimento.")
    if not isinstance(category, str) or not category.strip():
        raise ValueError("Informe uma categoria valida.")
    if not isinstance(unit, str) or not unit.strip():
        raise ValueError("Informe uma unidade de medida.")

    if isinstance(quantity, bool):
        raise ValueError("A quantidade precisa ser numerica.")
    try:
        numeric_quantity = float(quantity)
    except (TypeError, ValueError) as exc:
        raise ValueError("A quantidade precisa ser numerica.") from exc

    if not (numeric_quantity > 0) or not math.isfinite(numeric_quantity):
        raise ValueError("A quantidade deve ser um numero finito maior que zero.")

    normalize_expiration_date(expiration_date)
    return numeric_quantity


def add_food(name, quantity, unit, expiration_date, category):
    numeric_quantity = validate_food(
        name, quantity, unit, expiration_date, category
    )
    food = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "quantity": numeric_quantity,
        "unit": unit.strip(),
        "expiration_date": normalize_expiration_date(expiration_date),
        "category": category.strip(),
        "status": "disponivel",
        "created_at": datetime.now().isoformat()
    }
    inventory = load_inventory()
    inventory.append(food)
    save_inventory(inventory)
    return food


def update_food(food_id, **changes):
    allowed = {"name", "quantity", "unit", "expiration_date", "category"}
    if not changes:
        raise ValueError("Nenhuma informacao foi enviada para atualizacao.")
    if set(changes) - allowed:
        raise ValueError("Campo de atualizacao invalido.")

    inventory = load_inventory()
    for index, food in enumerate(inventory):
        if food.get("id") != food_id:
            continue

        updated = {**food, **changes}
        updated["quantity"] = validate_food(
            updated.get("name"),
            updated.get("quantity"),
            updated.get("unit"),
            updated.get("expiration_date"),
            updated.get("category")
        )
        updated["expiration_date"] = normalize_expiration_date(
            updated["expiration_date"]
        )
        inventory[index] = updated
        save_inventory(inventory)
        return updated

    raise ValueError("Alimento nao encontrado.")


def get_inventory(only_available=False):
    inventory = load_inventory()
    if only_available:
        return [food for food in inventory if food.get("status") == "disponivel"]
    return inventory


def get_food_by_id(food_id):
    return next(
        (food for food in load_inventory() if food.get("id") == food_id),
        None
    )


def update_food_status(food_id, status):
    if status not in VALID_STATUSES:
        raise ValueError("Status informado invalido.")
    inventory = load_inventory()
    for food in inventory:
        if food.get("id") == food_id:
            food["status"] = status
            save_inventory(inventory)
            return True
    return False


def mark_as_consumed(food_id):
    return update_food_status(food_id, "consumido")


def mark_as_discarded(food_id):
    return update_food_status(food_id, "descartado")


def remove_food(food_id):
    inventory = load_inventory()
    updated = [food for food in inventory if food.get("id") != food_id]
    if len(updated) == len(inventory):
        return False
    save_inventory(updated)
    return True


def generate_agent_report(today=None):
    from .expiration import get_expiration_report

    inventory = get_inventory(only_available=True)
    if not inventory:
        return "A despensa esta vazia no momento."

    report = get_expiration_report(inventory, today=today)
    lines = ["=== ESTOQUE ATUAL DA DESPENSA (NAOPERDE) ==="]
    for item in report:
        food = get_food_by_id(item["id"])
        lines.append(
            f"- {food['name']}: {food['quantity']} {food['unit']} | "
            f"Categoria: {food['category']} | "
            f"Validade: {item['expiration_date']} | "
            f"Situacao: {item['status']}"
        )
    lines.append(
        "OBSERVACAO: a data cadastrada nao garante a seguranca do alimento. "
        "Considere armazenamento, embalagem e sinais de deterioracao."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    init_storage()
    print("Armazenamento do NaoPerde inicializado. Nenhum alimento de demonstracao foi cadastrado.")
