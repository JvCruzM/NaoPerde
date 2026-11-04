
import json
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONVERSATIONS_FILE = BASE_DIR / "data" / "conversations.json"


def load_conversations():
    CONVERSATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CONVERSATIONS_FILE.exists():
        return []
    try:
        with CONVERSATIONS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError("O historico de conversas esta corrompido.") from exc
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        raise ValueError("Formato invalido do historico de conversas.")
    return data


def save_conversations(conversations):
    if not isinstance(conversations, list):
        raise ValueError("As conversas devem ser uma lista.")
    CONVERSATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = CONVERSATIONS_FILE.with_suffix(".tmp")
    try:
        temporary.write_text(
            json.dumps(conversations, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(CONVERSATIONS_FILE)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def create_conversation(title="Nova conversa"):
    conversations = load_conversations()
    conversation = {
        "id": str(uuid.uuid4()),
        "title": title,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "messages": [],
    }
    conversations.insert(0, conversation)
    save_conversations(conversations)
    return conversation


def get_conversation(conversation_id):
    return next((c for c in load_conversations() if c.get("id") == conversation_id), None)


def add_message(conversation_id, role, content):
    if role not in {"user", "assistant"} or not isinstance(content, str):
        raise ValueError("Mensagem invalida.")
    conversations = load_conversations()
    for conversation in conversations:
        if conversation.get("id") == conversation_id:
            conversation.setdefault("messages", []).append({"role": role, "content": content})
            if role == "user" and len(conversation["messages"]) == 1:
                conversation["title"] = content.strip()[:42] or "Nova conversa"
            conversation["updated_at"] = datetime.now().isoformat(timespec="seconds")
            save_conversations(conversations)
            return conversation
    raise ValueError("Conversa nao encontrada.")


def delete_conversation(conversation_id):
    conversations = load_conversations()
    updated = [c for c in conversations if c.get("id") != conversation_id]
    if len(updated) == len(conversations):
        return False
    save_conversations(updated)
    return True
