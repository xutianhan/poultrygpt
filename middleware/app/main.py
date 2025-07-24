from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.services.semantic import KB_IDS, KB_NAMES, KB_VECS  # 触发加载

app = FastAPI(title="Poultry-Diagnose")

@app.on_event("startup")
async def startup_event():
    print(f"已加载 {len(KB_IDS)} 条症状向量到内存")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(chat_router)