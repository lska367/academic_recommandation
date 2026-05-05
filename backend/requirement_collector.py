import os
import uuid
from typing import Dict, Any, List, Optional, Generator
from dotenv import load_dotenv
from openai import OpenAI


class RequirementCollector:
    def __init__(self, api_key=None, base_url=None, model=None):
        load_dotenv()
        self.api_key = api_key or os.getenv("VOLCENGINE_API_KEY")
        self.base_url = base_url or os.getenv("VOLCENGINE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.model = model or os.getenv("CHAT_MODEL", "doubao-seed-2-0-lite-260215")
        if not self.api_key:
            raise ValueError("API key must be provided or set as VOLCENGINE_API_KEY environment variable")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.min_rounds = 3

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "round_count": 0,
            "phase": "collecting",
            "messages": [],
            "requirement_summary": "",
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def _build_proactive_question_prompt(self, round_count: int, conversation_history: List[Dict[str, str]]) -> str:
        history_text = "\n".join([
            f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}"
            for msg in conversation_history
        ])

        if round_count == 1:
            focus_guide = """你现在是第一轮追问。用户刚刚提出了一个研究主题，你需要：
1. 确认理解用户的研究主题
2. 询问更具体的研究方向或子领域
3. 了解用户的主要关注点

例如，如果用户说"深度学习"，你可以问：
"您对深度学习的哪个具体方向感兴趣？比如计算机视觉、自然语言处理、强化学习还是其他领域？您目前的主要研究目标是什么？\""""
        elif round_count == 2:
            focus_guide = """你现在是第二轮追问。用户已经说明了研究方向，你需要：
1. 了解用户关注的具体技术方法或算法
2. 询问时间范围偏好（近期进展还是经典方法）
3. 了解用户对论文类型的偏好（理论、实验、综述等）

例如：
"您更关注哪类技术方法？是Transformer架构、CNN、RNN还是其他？另外，您希望看到最新的研究进展（近1-2年）还是也包括经典方法？\""""
        else:
            focus_guide = """你现在是第三轮或后续追问。用户已经提供了较多信息，你需要：
1. 询问应用场景或具体使用需求
2. 了解用户对论文数量、语言等偏好
3. 总结已收集的需求信息，告知用户可以开始检索

例如：
"了解了！最后想确认一下：您是希望将这些方法应用到什么场景中？比如学术研究、工程实践还是教学参考？如果需求已经明确，我可以开始为您检索相关论文了。\""""

        prompt = f"""你是一位专业的学术研究助手，正在通过对话了解用户的论文检索需求，以便提供更精准的推荐。

对话历史：
{history_text}

{focus_guide}

请生成一段自然、友好的追问回复（150字以内），帮助进一步明确用户需求。不要重复用户已经说过的内容，要提出新的问题。"""

        return prompt

    def _build_summary_prompt(self, conversation_history: List[Dict[str, str]]) -> str:
        history_text = "\n".join([
            f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""根据以下对话历史，提取用户的研究需求并生成一个简洁的需求摘要，用于优化论文检索查询。

对话历史：
{history_text}

请提取以下信息并生成需求摘要：
1. 研究主题和具体方向
2. 关注的技术方法或算法
3. 时间范围偏好
4. 应用场景
5. 其他特殊要求

请直接输出需求摘要（200字以内），格式如下：
研究主题：...
具体方向：...
技术方法：...
时间范围：...
应用场景：...
特殊要求：...

综合检索查询：[一个整合了所有需求的优化检索查询语句]"""

        return prompt

    def generate_proactive_question(self, session_id: str, user_message: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        try:
            session["messages"].append({"role": "user", "content": user_message})
            session["round_count"] += 1
            round_count = session["round_count"]

            prompt = self._build_proactive_question_prompt(round_count, session["messages"])

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            assistant_reply = response.choices[0].message.content
            session["messages"].append({"role": "assistant", "content": assistant_reply})

            ready_for_search = round_count >= self.min_rounds
            requirement_summary = ""

            if ready_for_search:
                requirement_summary = self._generate_requirement_summary(session_id)

            return {
                "success": True,
                "response": assistant_reply,
                "round_count": round_count,
                "ready_for_search": ready_for_search,
                "requirement_summary": requirement_summary,
            }
        except Exception as e:
            if session["messages"] and session["messages"][-1]["role"] == "user":
                session["messages"].pop()
                session["round_count"] = max(0, session["round_count"] - 1)
            return {"success": False, "error": str(e)}

    def generate_proactive_question_stream(self, session_id: str, user_message: str) -> Generator[Dict[str, Any], None, None]:
        session = self.get_session(session_id)
        if not session:
            yield {"event": "conversation_error", "data": {"success": False, "error": "Session not found"}}
            return

        try:
            session["messages"].append({"role": "user", "content": user_message})
            session["round_count"] += 1
            round_count = session["round_count"]

            prompt = self._build_proactive_question_prompt(round_count, session["messages"])

            yield {
                "event": "conversation_start",
                "data": {
                    "stage": "conversation_start",
                    "message": "正在思考如何追问...",
                    "round_count": round_count,
                }
            }

            full_content = ""
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
                stream=True
            )

            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content_piece = chunk.choices[0].delta.content
                    full_content += content_piece
                    yield {
                        "event": "conversation_chunk",
                        "data": {
                            "stage": "conversation_chunk",
                            "content": content_piece,
                            "full_content": full_content,
                        }
                    }

            session["messages"].append({"role": "assistant", "content": full_content})

            ready_for_search = round_count >= self.min_rounds
            requirement_summary = ""

            if ready_for_search:
                requirement_summary = self._generate_requirement_summary(session_id)

            yield {
                "event": "conversation_complete",
                "data": {
                    "stage": "conversation_complete",
                    "success": True,
                    "response": full_content,
                    "round_count": round_count,
                    "ready_for_search": ready_for_search,
                    "requirement_summary": requirement_summary,
                }
            }
        except Exception as e:
            if session["messages"] and session["messages"][-1]["role"] == "user":
                session["messages"].pop()
                session["round_count"] = max(0, session["round_count"] - 1)
            yield {
                "event": "conversation_error",
                "data": {"success": False, "error": str(e)}
            }

    def _generate_requirement_summary(self, session_id: str) -> str:
        session = self.get_session(session_id)
        if not session:
            return ""

        prompt = self._build_summary_prompt(session["messages"])

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            summary = response.choices[0].message.content
            session["requirement_summary"] = summary
            return summary
        except Exception as e:
            print(f"生成需求摘要失败: {e}")
            user_messages = [msg["content"] for msg in session["messages"] if msg["role"] == "user"]
            summary = " ".join(user_messages)
            session["requirement_summary"] = summary
            return summary

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
