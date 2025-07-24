# build_feature_vec.py
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import pickle

MODEL_NAME = "moka-ai/m3e-small"
CSV_PATH   = "feature.csv"
VEC_PATH   = "feature_vec.pkl"

def main():
    # 1. 加载模型
    model = SentenceTransformer(MODEL_NAME)

    # 2. 读 CSV
    df = pd.read_csv(CSV_PATH)
    names = df["featureName"].astype(str).tolist()
    ids   = df["featureID"].astype(str).tolist()

    # 3. 批量编码
    vecs = model.encode(names, normalize_embeddings=True, show_progress_bar=True)

    # 4. 持久化
    with open(VEC_PATH, "wb") as f:
        pickle.dump({"ids": ids, "names": names, "vecs": vecs}, f)
    print(f"已保存 {len(names)} 个向量到 {VEC_PATH}")

if __name__ == "__main__":
    main()