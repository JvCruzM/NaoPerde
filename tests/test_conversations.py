import pytest
from src import conversations


@pytest.fixture
def conversation_storage(tmp_path, monkeypatch):
    path = tmp_path / "data" / "conversations.json"
    monkeypatch.setattr(conversations, "CONVERSATIONS_FILE", path)
    return path


def test_create_and_persist_conversation(conversation_storage):
    item = conversations.create_conversation()
    loaded = conversations.load_conversations()
    assert loaded[0]["id"] == item["id"]
    assert loaded[0]["messages"] == []


def test_add_message_updates_title_and_history(conversation_storage):
    item = conversations.create_conversation()
    conversations.add_message(item["id"], "user", "Como aproveitar tomates?")
    conversations.add_message(item["id"], "assistant", "Você pode preparar um molho.")
    saved = conversations.get_conversation(item["id"])
    assert saved["title"] == "Como aproveitar tomates?"
    assert [m["role"] for m in saved["messages"]] == ["user", "assistant"]


def test_delete_conversation(conversation_storage):
    item = conversations.create_conversation()
    assert conversations.delete_conversation(item["id"]) is True
    assert conversations.load_conversations() == []
    assert conversations.delete_conversation(item["id"]) is False


def test_reject_invalid_message(conversation_storage):
    item = conversations.create_conversation()
    with pytest.raises(ValueError):
        conversations.add_message(item["id"], "system", "no")
