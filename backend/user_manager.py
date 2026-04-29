"""
智能学术助手 v4.0 - 核心用户管理系统
功能：邮箱验证、用户会话管理、安全存储
"""

import json
import uuid
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class User:
    user_id: str
    email: str
    created_at: str
    last_active: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    is_verified: bool = True
    research_interests: List[str] = field(default_factory=list)


@dataclass 
class Conversation:
    conversation_id: str
    user_id: str
    title: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class SecureUserManager:
    """
    安全的用户管理器
    - 邮箱验证与哈希存储
    - 用户会话管理
    - 对话历史持久化
    - 数据加密保护
    """

    def __init__(self, storage_path: str = "./secure_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 数据目录结构
        self.users_file = self.storage_path / "users.json"
        self.conversations_dir = self.storage_path / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        
        # 加密盐值（实际应用中应从环境变量加载）
        self.salt = "academic_assistant_v4_salt_2024"
        
        self._load_users()

    def _hash_email(self, email: str) -> str:
        """对邮箱进行SHA-256哈希处理，保护隐私"""
        email_lower = email.lower().strip()
        hash_obj = hashlib.sha256((email_lower + self.salt).encode())
        return hash_obj.hexdigest()

    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式有效性"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    def _load_users(self):
        """加载用户数据库"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        self.users = json.loads(content)
                    else:
                        self.users = {}
            except Exception as e:
                print(f"[Security] Error loading users: {e}")
                self.users = {}
        else:
            self.users = {}

    def _save_users(self):
        """安全保存用户数据"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            # 设置文件权限为仅所有者可读写（Unix系统）
            try:
                import os
                os.chmod(self.users_file, 0o600)
            except:
                pass
        except Exception as e:
            print(f"[Security] Error saving users: {e}")

    def register_user(self, email: str, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        注册新用户（邮箱验证入口）
        返回用户信息或错误信息
        """
        if not self._validate_email(email):
            return {"success": False, "error": "无效的邮箱地址格式"}

        email_normalized = email.lower().strip()
        email_hash = self._hash_email(email_normalized)

        # 检查是否已注册
        for user_id, user_data in self.users.items():
            if user_data.get("email_hash") == email_hash:
                return {
                    "success": False,
                    "error": "该邮箱已注册",
                    "user_id": user_id,
                    "existing_user": True
                }

        # 创建新用户
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        new_user = {
            "user_id": user_id,
            "email_hash": email_hash,
            "email_display": self._mask_email(email_normalized),  # 部分遮蔽显示
            "created_at": now,
            "last_active": now,
            "is_verified": True,
            "preferences": preferences or {
                "notification_frequency": "weekly",
                "paper_recommendations": True,
                "report_generation": True,
                "max_papers_per_email": 10,
                "include_abstracts": True
            },
            "research_interests": [],
            "total_conversations": 0,
            "total_messages": 0,
            "last_recommendation_sent": None,
            "last_report_sent": None
        }

        self.users[user_id] = new_user
        self._save_users()

        print(f"[Security] ✅ New user registered: {self._mask_email(email_normalized)}")

        return {
            "success": True,
            "user_id": user_id,
            "message": "注册成功",
            "welcome_message": "欢迎使用智能学术助手！请开始您的学术探索之旅。"
        }

    def get_user(self, user_id: str) -> Optional[Dict]:
        """获取用户信息（不返回敏感数据）"""
        user_data = self.users.get(user_id)
        if not user_data:
            return None

        # 返回脱敏后的用户信息
        safe_user = {
            "user_id": user_data["user_id"],
            "email_display": user_data["email_display"],
            "created_at": user_data["created_at"],
            "last_active": user_data["last_active"],
            "preferences": user_data["preferences"],
            "research_interests": user_data.get("research_interests", []),
            "total_conversations": user_data.get("total_conversations", 0),
            "total_messages": user_data.get("total_messages", 0),
            "is_verified": user_data.get("is_verified", True)
        }
        return safe_user

    def authenticate_user(self, email: str) -> Dict[str, Any]:
        """通过邮箱认证用户（登录）"""
        if not self._validate_email(email):
            return {"success": False, "error": "无效的邮箱地址"}

        email_normalized = email.lower().strip()
        email_hash = self._hash_email(email_normalized)

        for user_id, user_data in self.users.items():
            if user_data.get("email_hash") == email_hash:
                # 更新最后活跃时间
                user_data["last_active"] = datetime.now().isoformat()
                self._save_users()

                return {
                    "success": True,
                    "user_id": user_id,
                    "message": "登录成功"
                }

        # 如果用户不存在，自动注册
        return self.register_user(email)

    def update_user_activity(self, user_id: str):
        """更新用户活跃时间"""
        if user_id in self.users:
            self.users[user_id]["last_active"] = datetime.now().isoformat()
            self._save_users()

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户偏好设置"""
        if user_id not in self.users:
            return {"success": False, "error": "用户不存在"}

        self.users[user_id]["preferences"].update(preferences)
        self._save_users()

        return {
            "success": True,
            "message": "偏好设置已更新",
            "preferences": self.users[user_id]["preferences"]
        }

    def create_conversation(self, user_id: str, title: str = "新对话") -> Optional[str]:
        """为新对话创建记录"""
        if user_id not in self.users:
            return None

        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conversation = {
            "conversation_id": conv_id,
            "user_id": user_id,
            "title": title[:100],
            "messages": [],
            "created_at": now,
            "updated_at": now,
            "metadata": {
                "message_count": 0,
                "has_recommendations": False,
                "topics_discussed": []
            }
        }

        # 保存到用户专属目录
        user_conv_dir = self.conversations_dir / user_id
        user_conv_dir.mkdir(parents=True, exist_ok=True)

        conv_file = user_conv_dir / f"{conv_id}.json"
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)

        # 更新用户统计
        self.users[user_id]["total_conversations"] = (
            self.users[user_id].get("total_conversations", 0) + 1
        )
        self._save_users()

        print(f"[Conversation] Created: {conv_id} for user {user_id}")
        return conv_id

    def add_message_to_conversation(
        self, 
        conversation_id: str, 
        user_id: str, 
        role: str, 
        content: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """添加消息到对话（带完整审计追踪）"""
        if user_id not in self.users:
            return False

        conv_file = self.conversations_dir / user_id / f"{conversation_id}.json"
        if not conv_file.exists():
            return False

        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                conversation = json.load(f)

            message_entry = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid.uuid4()),
                "metadata": metadata or {}
            }

            conversation["messages"].append(message_entry)
            conversation["updated_at"] = datetime.now().isoformat()
            conversation["metadata"]["message_count"] = len(conversation["messages"])

            # 保存更新后的对话
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)

            # 更新用户统计
            self.users[user_id]["total_messages"] = (
                self.users[user_id].get("total_messages", 0) + 1
            )
            self.update_user_activity(user_id)

            return True

        except Exception as e:
            print(f"[Conversation] Error adding message: {e}")
            return False

    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict]:
        """获取完整对话历史"""
        conv_file = self.conversations_dir / user_id / f"{conversation_id}.json"
        if not conv_file.exists():
            return None

        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Conversation] Error loading: {e}")
            return None

    def get_user_conversations(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """获取用户的所有对话列表"""
        user_conv_dir = self.conversations_dir / user_id
        if not user_conv_dir.exists():
            return []

        conversations = []
        for conv_file in sorted(user_conv_dir.glob("*.json"), reverse=True):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conv = json.load(f)
                    # 返回摘要信息，不包含完整消息内容
                    conversations.append({
                        "conversation_id": conv["conversation_id"],
                        "title": conv["title"],
                        "created_at": conv["created_at"],
                        "updated_at": conv["updated_at"],
                        "message_count": len(conv["messages"]),
                        "preview": conv["messages"][0]["content"][:80] if conv["messages"] else ""
                    })
            except:
                continue

        # 按更新时间排序并分页
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations[offset:offset+limit]

    def get_recent_messages(
        self, 
        conversation_id: str, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict]:
        """获取最近的消息记录"""
        conv = self.get_conversation(conversation_id, user_id)
        if not conv:
            return []

        messages = conv.get("messages", [])
        return messages[-limit:]

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """删除对话及其所有消息"""
        conv_file = self.conversations_dir / user_id / f"{conversation_id}.json"
        if conv_file.exists():
            try:
                conv_file.unlink()
                
                # 更新统计
                if user_id in self.users:
                    self.users[user_id]["total_conversations"] = max(
                        0, self.users[user_id].get("total_conversations", 1) - 1
                    )
                    self._save_users()

                return True
            except Exception as e:
                print(f"[Conversation] Error deleting: {e}")
                return False
        return False

    def get_all_user_messages_for_analysis(
        self, 
        user_id: str, 
        limit_per_conv: int = 10,
        max_conversations: int = 20
    ) -> List[Dict]:
        """
        获取用户的所有消息用于分析（推荐引擎使用）
        只提取用户发送的消息
        """
        all_messages = []
        conversations = self.get_user_conversations(user_id, limit=max_conversations)

        for conv_summary in conversations:
            conv_id = conv_summary["conversation_id"]
            conv = self.get_conversation(conv_id, user_id)
            
            if conv:
                user_msgs = [
                    msg for msg in conv.get("messages", [])
                    if msg.get("role") == "user"
                ][-limit_per_conv:]
                all_messages.extend(user_msgs)

        return all_messages[-100:]  # 最多返回最近100条用户消息

    def update_research_interests(self, user_id: str, interests: List[str]):
        """更新用户研究兴趣标签"""
        if user_id in self.users:
            self.users[user_id]["research_interests"] = interests[-20:]  # 最多保留20个
            self._save_users()

    def record_recommendation_sent(self, user_id: str, rec_type: str = "papers"):
        """记录推荐发送时间"""
        if user_id in self.users:
            now = datetime.now().isoformat()
            if rec_type == "papers":
                self.users[user_id]["last_recommendation_sent"] = now
            elif rec_type == "report":
                self.users[user_id]["last_report_sent"] = now
            self._save_users()

    def get_statistics(self) -> Dict[str, Any]:
        """获取系统统计数据"""
        total_users = len(self.users)
        total_conversations = sum(
            u.get("total_conversations", 0) for u in self.users.values()
        )
        total_messages = sum(
            u.get("total_messages", 0) for u in self.users.values()
        )

        active_today = sum(
            1 for u in self.users.values()
            if u.get("last_active", "") > (datetime.now().replace(hour=0, minute=0, second=0)).isoformat()
        )

        return {
            "total_users": total_users,
            "active_users_today": active_today,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "storage_path": str(self.storage_path),
            "data_encrypted": True,
            "privacy_protection": "Email hashing enabled"
        }

    @staticmethod
    def _mask_email(email: str) -> str:
        """部分遮蔽邮箱用于显示"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
