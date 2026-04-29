import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Message:
    role: str
    content: str
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Conversation:
    conversation_id: str
    user_id: str
    title: str
    messages: List[Dict[str, str]]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConversationManager:
    def __init__(self, storage_path: str = "./data/conversations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.conversations_file = self.storage_path / "conversations.json"
        self._load_conversations()

    def _load_conversations(self):
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
            except Exception as e:
                print(f"Error loading conversations: {e}")
                self.conversations = {}
        else:
            self.conversations = {}

    def _save_conversations(self):
        try:
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving conversations: {e}")

    def create_conversation(self, user_id: str = "default", title: str = "新对话") -> str:
        conversation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conversation = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "title": title,
            "messages": [],
            "created_at": now,
            "updated_at": now,
            "metadata": {}
        }

        self.conversations[conversation_id] = conversation
        self._save_conversations()
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str) -> bool:
        if conversation_id not in self.conversations:
            return False

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        self.conversations[conversation_id]["messages"].append(message)
        self.conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
        self._save_conversations()
        return True

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        return self.conversations.get(conversation_id)

    def get_all_conversations(self, user_id: str = None) -> List[Dict]:
        conversations = list(self.conversations.values())
        if user_id:
            conversations = [c for c in conversations if c.get("user_id") == user_id]
        return sorted(conversations, key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        conv = self.conversations.get(conversation_id)
        if not conv:
            return []
        messages = conv.get("messages", [])
        return messages[-limit:]

    def update_title(self, conversation_id: str, title: str) -> bool:
        if conversation_id not in self.conversations:
            return False
        self.conversations[conversation_id]["title"] = title
        self.conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
        self._save_conversations()
        return True

    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            self._save_conversations()
            return True
        return False

    def get_user_interests(self, user_id: str = "default") -> List[str]:
        conversations = self.get_all_conversations(user_id)
        all_messages = []
        for conv in conversations:
            messages = conv.get("messages", [])
            for msg in messages:
                if msg.get("role") == "user":
                    all_messages.append(msg.get("content", ""))

        return all_messages[-50:]

    def get_statistics(self) -> Dict[str, Any]:
        total_conversations = len(self.conversations)
        total_messages = sum(len(c.get("messages", [])) for c in self.conversations.values())
        user_ids = set(c.get("user_id", "default") for c in self.conversations.values())

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "unique_users": len(user_ids),
            "storage_path": str(self.storage_path)
        }
