from types import SimpleNamespace
import pytest
from src import agent as agent_module
from src.agent import NaoPerdeAgent, _normalizar_estoque


def sample_food():
    return {
        "id": "abc", "name": "Tomate", "quantity": 2,
        "unit": "unidades", "category": "Hortifruti",
        "expiration_date": "2026-11-10", "status": "disponivel"
    }


def test_agent_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        NaoPerdeAgent(api_key=None)


def test_normalize_stock_uses_canonical_schema():
    normalized = _normalizar_estoque([sample_food()])
    assert normalized[0]["name"] == "Tomate"
    assert normalized[0]["days_remaining"] >= 0


def test_normalize_stock_rejects_bad_quantity():
    item = sample_food()
    item["quantity"] = "dois"
    with pytest.raises(ValueError, match="numerica"):
        _normalizar_estoque([item])


def test_chat_with_mocked_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    monkeypatch.setattr(agent_module, "Groq", lambda api_key: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=None))))
    agent = NaoPerdeAgent(api_key="fake-key")
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Priorize o tomate."))]
        )

    agent.client.chat.completions.create = fake_create
    answer = agent.chat("O que devo usar?", [sample_food()], session_id="sessao-1")
    assert answer == "Priorize o tomate."
    assert "Tomate" in captured["messages"][-1]["content"]
    assert len(agent._historicos["sessao-1"]) == 2


def test_history_is_per_session_and_clearable(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    monkeypatch.setattr(agent_module, "Groq", lambda api_key: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=None))))
    agent = NaoPerdeAgent(api_key="fake-key")
    agent._historicos["a"] = [{"role": "user", "content": "x"}]
    agent._historicos["b"] = [{"role": "user", "content": "y"}]
    agent.limpar_historico("a")
    assert "a" not in agent._historicos
    assert "b" in agent._historicos
