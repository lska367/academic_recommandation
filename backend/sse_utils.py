
import json
import asyncio
from typing import AsyncGenerator, Callable, Dict, Any, Optional
from fastapi import HTTPException


class SSEHandler:
    def __init__(self):
        self.event_id = 0
    
    def next_event_id(self) -> str:
        self.event_id += 1
        return str(self.event_id)
    
    def format_event(self, event: str, data: Dict[str, Any], event_id: Optional[str] = None) -> str:
        if event_id is None:
            event_id = self.next_event_id()
        
        lines = [
            f"id: {event_id}",
            f"event: {event}",
            f"data: {json.dumps(data, ensure_ascii=False)}",
            ""
        ]
        return "\n".join(lines)
    
    async def send_event(self, event_type: str, data: Dict[str, Any], event_id: Optional[str] = None):
        if event_id is None:
            event_id = self.next_event_id()
        message = self.format_event(event_type, data, event_id)
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


sse_handler = SSEHandler()


def create_sse_response(event: str, data: Dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def event_generator(event_type: str, data: Dict[str, Any]) -> AsyncGenerator[str, None]:
    yield create_sse_response(event_type, data)


async def progress_callback(stage: str, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    event_data = {
        "stage": stage,
        "message": message,
    }
    if data:
        event_data.update(data)
    return event_data
