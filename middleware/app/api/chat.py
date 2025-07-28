from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services import redis_service, neo4j_service, semantic
from rank_bm25 import BM25Okapi
import numpy as np

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/diagnose", response_model=ChatResponse)
def diagnose_endpoint(req: ChatRequest):
    uid, sid = req.user_id, req.session_id
    state = redis_service.get_session(uid, sid)
    turn = redis_service.incr_turn(uid, sid)  # 先自增轮次

    logger.info(f"Step 1: User ID: {uid}, Session ID: {sid}, Turn: {turn}, Intent: {req.intent}, Entities: {req.entities}")

    # 1. 把 Dify 给的实体做一次标准化 / 相似度校验
    confirmed = []
    pending = None
    for ent in req.entities or []:
        norm = semantic.normalize_symptom(ent)
        if norm:
            confirmed.append(norm)
        else:
            pending = ent  # 需要澄清

    logger.info(f"Step 2: Normalized entities: {confirmed}, Pending clarification: {pending}")

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
        logger.info(f"Step 3: Clarification needed for: {pending}")
        return ChatResponse(
            reply=question,
            session_state=redis_service.get_session(uid, sid),
            need_clarify=True,
        )

    # 4. 无需澄清 → 用已确认实体查询 Redis
    user_symptoms = state.get("entities", [])
    all_disease_symptoms = redis_service.get_all_disease_symptoms()

    logger.info(f"Step 4: User symptoms: {user_symptoms}")
    logger.info(f"Step 4: Loaded disease symptoms: {all_disease_symptoms}")

    # 5. 计算相似度
    disease_ids = list(all_disease_symptoms.keys())
    disease_symptoms = [disease["symptoms"] for disease in all_disease_symptoms.values()]
    bm25 = BM25Okapi(disease_symptoms)
    similarity_scores = bm25.get_scores(user_symptoms)
    threshold = 0.7  # 相似度阈值
    diagnosed_diseases = [all_disease_symptoms[disease_id] for disease_id, score in zip(disease_ids, similarity_scores) if score >= threshold]

    logger.info(f"Step 5: Similarity scores: {similarity_scores}")
    logger.info(f"Step 5: Diagnosed diseases: {[disease['disease_name'] for disease in diagnosed_diseases]}")

    # 6. 如果确诊疾病，生成诊断报告
    if diagnosed_diseases:
        report = ""
        for disease in diagnosed_diseases:
            report += generate_diagnosis_report(user_symptoms, disease["disease_name"])
        redis_service.set_session(uid, sid, diagnosed=True, diseases=[disease["disease_name"] for disease in diagnosed_diseases])
        logger.info(f"Step 6: Diagnosis report: {report}")
        return ChatResponse(
            reply=report,
            session_state=redis_service.get_session(uid, sid),
            need_clarify=False,
        )

    # 7. 如果未确诊，继续澄清症状
    suggested_symptoms = neo4j_service.get_suggested_symptoms(disease_ids, state.get("entities", []))
    question = f"根据症状 {', '.join(user_symptoms)}，可能的疾病有：{', '.join([disease['disease_name'] for disease in all_disease_symptoms.values()])}。请提供更多症状以缩小范围。建议描述以下症状：{', '.join(suggested_symptoms)}"
    redis_service.set_session(uid, sid, last_question=question)
    logger.info(f"Step 7: Suggested symptoms: {suggested_symptoms}")
    return ChatResponse(
        reply=question,
        session_state=redis_service.get_session(uid, sid),
        need_clarify=True,
    )