# app/services/semantic.py
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

VEC_PATH   = Path(__file__).with_name("feature_vec.pkl")
SIM_THRESH = 0.7

# 启动时一次性加载
with open(VEC_PATH, "rb") as f:
    data = pickle.load(f)
KB_IDS, KB_NAMES, KB_VECS = data["ids"], data["names"], np.array(data["vecs"])

# 轻量级在线编码器
_model = None
def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("moka-ai/m3e-small")
    return _model

def normalize_symptom(raw: str) -> tuple[str, float] | None:
    raw = raw.strip()
    if not raw:
        return None
    vec = _get_model().encode([raw], normalize_embeddings=True)
    sims = np.dot(KB_VECS, vec.T).flatten()
    idx = int(np.argmax(sims))
    score = float(sims[idx])
    return (KB_NAMES[idx], score) if score >= SIM_THRESH else None