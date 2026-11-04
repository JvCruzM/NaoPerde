
from datetime import date, datetime

def analyze_expiration(food, today=None):

    if today is None:
        today = date.today()

    if isinstance(today, datetime):
        today = today.date()

    if not isinstance(today, date):
        raise ValueError("A data de referencia deve ser valida.")

    try:
        expiration = food["expiration_date"]

        if isinstance(expiration, datetime):
            expiration = expiration.date()

        elif isinstance(expiration, str):
            expiration = date.fromisoformat(expiration)

        if not isinstance(expiration, date):
            raise ValueError

    except (KeyError, TypeError, ValueError):
        raise ValueError(
            f"Data de validade invalida para o alimento "
            f"{food.get('name', 'desconhecido')}."
        )

    days_remaining = (expiration - today).days

    if days_remaining < 0:
        status = "Data expirada"
        priority = 0

    elif days_remaining == 0:
        status = "Vence hoje"
        priority = 1

    elif days_remaining <= 3:
        status = "Atencao imediata"
        priority = 2

    elif days_remaining <= 7:
        status = "Proximo do vencimento"
        priority = 3

    else:
        status = "Dentro do prazo informado"
        priority = 4

    return {
        "id": food["id"],
        "name": food["name"],
        "expiration_date": expiration.isoformat(),
        "days_remaining": days_remaining,
        "status": status,
        "priority": priority
    }


def get_expiration_report(inventory, today=None):

    report = [
        analyze_expiration(food, today)
        for food in inventory
        if food.get("status") == "disponivel"
    ]

    return sorted(
        report,
        key=lambda item: (
            item["priority"],
            item["days_remaining"]
        )
    )


def get_expiring_foods(inventory, days=7, today=None):

    if not isinstance(days, int) or isinstance(days, bool) or days < 0:
        raise ValueError("O periodo deve ser um numero inteiro nao negativo.")

    report = get_expiration_report(inventory, today)

    return [
        food for food in report
        if 0 <= food["days_remaining"] <= days
    ]
