
from datetime import date, datetime


def _parse_date(value, food_name="desconhecido"):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            pass
    raise ValueError(f"Data de validade invalida para o alimento {food_name}.")


def analyze_expiration(food, today=None):
    if not isinstance(food, dict):
        raise ValueError("O alimento precisa ser um dicionario.")
    if today is None:
        today = date.today()
    if isinstance(today, datetime):
        today = today.date()
    if not isinstance(today, date):
        raise ValueError("A data de referencia deve ser valida.")

    expiration = _parse_date(food.get("expiration_date"), food.get("name", "desconhecido"))
    if not food.get("id") or not food.get("name"):
        raise ValueError("O alimento precisa possuir id e name.")

    days = (expiration - today).days
    if days < 0:
        status, priority = "Data expirada", 0
    elif days == 0:
        status, priority = "Vence hoje", 1
    elif days <= 3:
        status, priority = "Atencao imediata", 2
    elif days <= 7:
        status, priority = "Proximo do vencimento", 3
    else:
        status, priority = "Dentro do prazo informado", 4

    return {
        "id": food["id"],
        "name": food["name"],
        "expiration_date": expiration.isoformat(),
        "days_remaining": days,
        "status": status,
        "priority": priority
    }


def get_expiration_report(inventory, today=None):
    if not isinstance(inventory, (list, tuple)):
        raise ValueError("O estoque deve ser uma lista de alimentos.")
    report = [
        analyze_expiration(food, today)
        for food in inventory
        if food.get("status") == "disponivel"
    ]
    return sorted(report, key=lambda item: (item["priority"], item["days_remaining"]))


def get_expiring_foods(inventory, days=7, today=None):
    if not isinstance(days, int) or isinstance(days, bool) or days < 0:
        raise ValueError("O periodo deve ser um numero inteiro nao negativo.")
    return [
        item for item in get_expiration_report(inventory, today)
        if 0 <= item["days_remaining"] <= days
    ]
