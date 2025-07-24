from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services import redis_service, neo4j_service, semantic

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    uid, sid = req.user_id, req.session_id
    state = redis_service.get_session(uid, sid)
    turn = redis_service.incr_turn(uid, sid)  # 先自增轮次

    # 1. 把 Dify 给的实体做一次标准化 / 相似度校验
    confirmed = []
    pending = None
    for ent in req.entities or []:
        norm = semantic.normalize_symptom(ent)
        if norm:
            confirmed.append(norm)
        else:
            pending = ent  # 需要澄清

    # 2. 更新 Redis 状态
    redis_service.set_session(
        uid, sid,
        intent=req.intent,
        entities=list(set(state.get("entities", []) + confirmed)),
        pending=pending,
    )

    # 3. 如果需要澄清
    if pending:
        question = f"您提到的“{pending}”暂未识别，请确认具体症状？"
        redis_service.set_session(uid, sid, last_question=question)
        return ChatResponse(
            reply=question,
            session_state=redis_service.get_session(uid, sid),
            need_clarify=True,
        )

    # 4. 无需澄清 → 用已确认实体查询 Neo4j
    diseases = []
    for sym in state.get("entities", []):
        diseases += neo4j_service.get_diseases_by_symptom(sym)
    diseases = list({d["disease"] for d in diseases})[:5]

    reply = f"根据症状 {', '.join(state.get('entities', []))}，可能疾病：{', '.join(diseases)}"
    redis_service.set_session(uid, sid, last_question=reply)
    return ChatResponse(
        reply=reply,
        session_state=redis_service.get_session(uid, sid),
        need_clarify=False,
    )