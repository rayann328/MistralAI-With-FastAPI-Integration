from collections import deque
from typing import Deque, Dict, List, Optional
import time
from dataclasses import dataclass
import uuid

@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: float

class HistoryStore:
    def __init__(self, max_size: int = 6, retention_hours: int = 24):
        self.sessions: Dict[str, Deque[Message]] = {}
        self.max_size = max_size
        self.retention_seconds = retention_hours * 3600
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_size)
        
        self.sessions[session_id].append(Message(role=role, content=content, timestamp=time.time()))
    
    def get_messages(self, session_id: str, max_messages: Optional[int] = None) -> List[Message]:
        if session_id not in self.sessions:
            return []
        
        messages = list(self.sessions[session_id])
        if max_messages:
            messages = messages[-max_messages:]
        
        return messages
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        messages = self.get_messages(session_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def clear_history(self, session_id: str) -> bool:
        if session_id in self.sessions:
            self.sessions[session_id].clear()
            return True
        return False
    
    def cleanup_old_sessions(self):
        """Remove sessions that haven't been active beyond retention period"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, messages in self.sessions.items():
            if messages and (current_time - messages[-1].timestamp) > self.retention_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def generate_session_id(self) -> str:
        return str(uuid.uuid4())# history.py
"""
This is the history.py file
"""

