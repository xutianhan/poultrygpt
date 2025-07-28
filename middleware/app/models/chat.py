from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str  # 来自 Dify
    intent: Optional[str] = None  # 来自 Dify
    entities: Optional[List[str]] = None  # 来自 Dify

class ChatResponse(BaseModel):
    reply: str
    session_state: Dict
    need_clarify: bool = False
    diagnosed: Optional[bool] = False  # 是否确诊
    diseases: Optional[List[str]] = None  # 确诊的疾病列表
    symptoms: Optional[List[str]] = None  # 确诊的疾病相关症状列表