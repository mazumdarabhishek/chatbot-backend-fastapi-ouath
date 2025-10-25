from typing import TypedDict, Optional, Dict, Any, List
from pydantic import BaseModel, Field



class AgentState(TypedDict):
    messages: List
    user_input: Optional[str]
    turns_to_compress: Optional[int]


class ChatRequest(BaseModel):
    user_input: str
    thread_id: Optional[str]
    

class ChatSessionRequest(BaseModel):
    page: int
    page_size: int