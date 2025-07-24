from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str
    intent: str | None = None          # 来自 Dify
    entities: list[str] | None = None  # 来自 Dify

class ChatResponse(BaseModel):
    reply: str
    session_state: dict
    need_clarify: bool = False