from pydantic import BaseModel
from typing import Optional, Dict, Any

class APIResponse(BaseModel):
    status: int
    message: str
    data: Optional[Dict[str, Any]] = None
    

class ChatResponse(BaseModel):
    response: str
    thread_id: str