from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.services.semantic import KB_IDS, KB_NAMES, KB_VECS  # 触发加载
from app.services.neo4j_service import preload_diseases_with_symptoms
import logging
from logging.handlers import TimedRotatingFileHandler
import os


# 确保日志文件夹存在
os.makedirs('/home/poultrygpt/middleware/logs', exist_ok=True)

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个 TimedRotatingFileHandler，每天生成一个新的日志文件
log_handler = TimedRotatingFileHandler(
    '/home/poultrygpt/middleware/logs/app.log',  # 日志文件路径
    when='midnight',  # 每天午夜轮转
    interval=1,  # 每天轮转一次
    backupCount=7,  # 保留7天的日志文件
    encoding='utf-8'
)
log_handler.suffix = "%Y-%m-%d"  # 文件名后缀格式
log_handler.setLevel(logging.INFO)

# 设置日志格式
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_format)

# 添加日志处理器
logger.addHandler(log_handler)


app = FastAPI(title="Poultry-Diagnose")

@app.on_event("startup")
async def startup_event():
    logger.info(f"已加载 {len(KB_IDS)} 条症状向量到内存")
    preload_diseases_with_symptoms()
    logger.info("所有疾病症状已加载到Redis中")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(chat_router)
