#!/bin/bash
set -euo pipefail

# 1. 环境
export MODEL_PATH=/opt/poultrygpt-chat-middleware/m3e-small
export REDIS_URL=redis://localhost:6379
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=Alex@20210901
WORKDIR=/home/poultrygpt

# 2. 容错启动依赖
echo ">>> 启动 Redis ..."
sudo systemctl start redis || echo "Redis 已运行或启动失败，继续..."

echo ">>> 启动 Neo4j ..."
sudo systemctl start neo4j || echo "Neo4j 已运行或启动失败，继续..."

# 3. 启动 FastAPI
echo ">>> 启动 FastAPI ..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info