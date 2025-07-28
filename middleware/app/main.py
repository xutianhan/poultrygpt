from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.services.semantic import KB_IDS, KB_NAMES, KB_VECS  # 触发加载

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Poultry-Diagnose")

@app.on_event("startup")
async def startup_event():
    logger.info(f"已加载 {len(KB_IDS)} 条症状向量到内存")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(chat_router)