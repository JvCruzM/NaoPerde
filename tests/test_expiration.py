from datetime import date, timedelta
import pytest
from src.expiration import analyze_expiration, get_expiration_report, get_expiring_foods

TODAY = date(2026, 11, 4)


def food(name, days, status="disponivel"):
    return {"id": name, "name": name, "expiration_date": TODAY + timedelta(days=days), "status": status}


@pytest.mark.parametrize("days,status,priority", [
    (-1, "Data expirada", 0),
    (0, "Vence hoje", 1),
    (2, "Atencao imediata", 2),
    (5, "Proximo do vencimento", 3),
    (8, "Dentro do prazo informado", 4),
])
def test_expiration_categories(days, status, priority):
    result = analyze_expiration(food("Item", days), TODAY)
    assert result["status"] == status
    assert result["priority"] == priority


def test_report_sorts_and_ignores_inactive():
    items = [food("Longa", 10), food("Hoje", 0), food("Consumido", -1, "consumido")]
    report = get_expiration_report(items, TODAY)
    assert [item["name"] for item in report] == ["Hoje", "Longa"]


def test_expiring_foods_excludes_already_expired():
    items = [food("Vencido", -1), food("Amanha", 1), food("Depois", 8)]
    assert [x["name"] for x in get_expiring_foods(items, 7, TODAY)] == ["Amanha"]


@pytest.mark.parametrize("days", [-1, 1.5, True])
def test_invalid_window(days):
    with pytest.raises(ValueError):
        get_expiring_foods([], days)
