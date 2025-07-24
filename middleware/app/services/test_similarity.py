import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

VEC_PATH = "feature_vec.pkl"
MODEL_NAME = "moka-ai/m3e-small"   # 如果需要二次编码

# 加载
with open(VEC_PATH, "rb") as f:
    data = pickle.load(f)
ids, names, vecs = data["ids"], data["names"], data["vecs"]

# 加载模型（仅用于在线编码新输入）
model = SentenceTransformer(MODEL_NAME)

# 测试一条
raw = "鸡冠肿胀"
vec = model.encode([raw], normalize_embeddings=True)
sims = np.dot(vecs, vec.T).flatten()
best_idx = int(np.argmax(sims))
print("输入：", raw)
print("最相似：", names[best_idx], "相似度：", sims[best_idx])