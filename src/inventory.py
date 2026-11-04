
import json
import uuid

from pathlib import Path
from datetime import datetime, date

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "inventory.json"

VALID_STATUSES = {
    "disponivel",
    "consumido",
    "descartado"
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

        if not isinstance(data, list):
            raise ValueError("Formato inválido do estoque.")

        return data

    except json.JSONDecodeError as error:
        raise ValueError(
            "O arquivo de estoque está corrompido. "
            "Os dados não foram alterados."
        ) from error


def save_inventory(inventory):

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = DATA_FILE.with_suffix(".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(
                inventory,
                file,
                ensure_ascii=False,
                indent=4
            )

        temporary_file.replace(DATA_FILE)

    except Exception:
        if temporary_file.exists():
            temporary_file.unlink()

        raise

def validate_food(name, quantity, unit, expiration_date, category):

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Informe um nome válido para o alimento.")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Informe uma categoria válida.")

    if not isinstance(unit, str) or not unit.strip():
        raise ValueError("Informe uma unidade de medida.")

    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValueError("A quantidade precisa ser numérica.")

    if quantity <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    if not isinstance(expiration_date, date):
        raise ValueError("Informe uma data de validade válida.")

    return quantity


def normalize_expiration_date(expiration_date):

    if isinstance(expiration_date, datetime):
        return expiration_date.date().isoformat()

    if isinstance(expiration_date, date):
        return expiration_date.isoformat()

    if isinstance(expiration_date, str):
        try:
            return date.fromisoformat(expiration_date).isoformat()
        except ValueError:
            raise ValueError(
                "Data inválida. Utilize o formato YYYY-MM-DD."
            )

    raise ValueError("Formato de data não suportado.")

def add_food(name, quantity, unit, expiration_date, category):

    quantity = validate_food(
        name,
        quantity,
        unit,
        expiration_date,
        category
    )

    food = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "quantity": quantity,
        "unit": unit.strip(),
        "expiration_date": normalize_expiration_date(
            expiration_date
        ),
        "category": category.strip(),
        "status": "disponivel",
        "created_at": datetime.now().isoformat()
    }

    inventory = load_inventory()
    inventory.append(food)

    save_inventory(inventory)

    return food

def update_food(food_id, **changes):

    allowed_fields = {
        "name",
        "quantity",
        "unit",
        "expiration_date",
        "category"
    }

    if not changes:
        raise ValueError("Nenhuma informação foi enviada para atualização.")

    if set(changes) - allowed_fields:
        raise ValueError("Campo de atualização inválido.")

    inventory = load_inventory()

    for food in inventory:

        if food["id"] == food_id:

            updated = food.copy()
            updated.update(changes)

            updated["quantity"] = validate_food(
                updated["name"],
                updated["quantity"],
                updated["unit"],
                normalize_expiration_date(
                    updated["expiration_date"]
                ),
                updated["category"]
            )

            updated["expiration_date"] = normalize_expiration_date(
                updated["expiration_date"]
            )

            for field in changes:
                food[field] = updated[field]

            save_inventory(inventory)

            return food

    raise ValueError("Alimento não encontrado.")

def get_inventory(only_available=False):

    inventory = load_inventory()

    if only_available:
        inventory = [
            food for food in inventory
            if food.get("status") == "disponivel"
        ]

    return inventory


def get_food_by_id(food_id):

    inventory = load_inventory()

    for food in inventory:
        if food["id"] == food_id:
            return food

    return None

def update_food_status(food_id, status):

    if status not in VALID_STATUSES:
        raise ValueError("Status informado inválido.")

    inventory = load_inventory()

    for food in inventory:

        if food["id"] == food_id:
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

    updated_inventory = [
        food for food in inventory
        if food["id"] != food_id
    ]

    if len(updated_inventory) == len(inventory):
        return False

    save_inventory(updated_inventory)

    return True

def generate_agent_report():

    inventory = get_inventory(only_available=True)

    if not inventory:
        return "A despensa está vazia no momento."

    today = date.today()

    expired = []
    urgent = []
    attention = []
    other = []

    for food in inventory:

        expiration = date.fromisoformat(
            food["expiration_date"]
        )

        days_remaining = (expiration - today).days

        line = (
            f"- {food['name']}: "
            f"{food['quantity']} {food['unit']} | "
            f"Categoria: {food['category']} | "
            f"Validade: {food['expiration_date']}"
        )

        if days_remaining < 0:
            expired.append(line)

        elif days_remaining <= 2:
            urgent.append(line)

        elif days_remaining <= 5:
            attention.append(line)

        else:
            other.append(line)

    report = (
        "=== ESTOQUE ATUAL DA DESPENSA (NÃO PERDE) ===\n"
    )

    if expired:
        report += (
            "\nALIMENTOS COM DATA DE VALIDADE EXPIRADA "
            "(NÃO RECOMENDAR O CONSUMO):\n"
            + "\n".join(expired)
            + "\n"
        )

    if urgent:
        report += (
            "\nALIMENTOS COM VENCIMENTO PRÓXIMO "
            "(ATÉ 2 DIAS):\n"
            + "\n".join(urgent)
            + "\n"
        )

    if attention:
        report += (
            "\nALIMENTOS EM ATENÇÃO "
            "(3 A 5 DIAS):\n"
            + "\n".join(attention)
            + "\n"
        )

    if other:
        report += (
            "\nDEMAIS ALIMENTOS "
            "(PRAZO INFORMADO SUPERIOR A 5 DIAS):\n"
            + "\n".join(other)
            + "\n"
        )

    report += (
        "\nOBSERVAÇÃO: As datas são informações cadastradas "
        "pelo usuário e não garantem a segurança sanitária "
        "dos alimentos. Considere também as condições de "
        "armazenamento e sinais de deterioração."
    )

    return report

if __name__ == "__main__":

    print("Inicializando armazenamento do NãoPerde...")

    init_storage()

    print("\nCadastrando alimentos de demonstração...")

    today = date.today()

    add_food(
        "Leite Integral",
        1,
        "litro",
        today,
        "Laticínios"
    )

    add_food(
        "Tomate",
        3,
        "unidades",
        today,
        "Hortifrúti"
    )

    add_food(
        "Queijo Prato",
        200,
        "gramas",
        date(2026, 11, 8),
        "Laticínios"
    )

    print("\nRelatório do estoque:\n")
    print(generate_agent_report())
