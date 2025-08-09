import redis, json
from app.config import settings

r = redis.from_url(settings.redis_url, decode_responses=True)

def _key(uid: str, sid: str) -> str:
    return f"{uid}:{sid}"

def get_session(uid: str, sid: str) -> dict:
    data = r.hgetall(_key(uid, sid)) or {}
    result = {}
    for k, v in data.items():
        if v == "null":  # 检查是否为字符串 "null"
            result[k] = None
        else:
            try:
                result[k] = json.loads(v)
            except json.JSONDecodeError:
                result[k] = v
    return result

def set_session(uid: str, sid: str, **fields):
    for k, v in fields.items():
        if v is None:
            v = "null"  # 将 None 转换为字符串 "null"
        elif isinstance(v, list) or isinstance(v, dict):
            v = json.dumps(v, ensure_ascii=False)
        r.hset(_key(uid, sid), k, v)

def incr_turn(uid: str, sid: str) -> int:
    return r.hincrby(_key(uid, sid), "turn", 1)

def get_all_disease_symptoms():
    disease_symptoms = r.hgetall("disease_symptoms")
    return {k: json.loads(v) for k, v in disease_symptoms.items()}

