#!/bin/bash
set +e  # 允许部分失败继续执行

echo ">>> 停止 FastAPI ..."
pkill -f "uvicorn.*app.main:app" || echo "FastAPI 未运行"

echo ">>> 强制释放 Python 内存 ..."
python3 - <<'PY' 2>/dev/null
import gc, sys, psutil, os
for proc in psutil.process_iter(['pid', 'cmdline']):
    cmd = ' '.join(proc.info['cmdline'] or [])
    if 'uvicorn' in cmd and 'app.main' in cmd:
        os.kill(proc.info['pid'], 9)
gc.collect()
PY

echo ">>> 停止 Redis ..."
sudo systemctl stop redis || echo "Redis 已停止"

echo ">>> 停止 Neo4j ..."
sudo systemctl stop neo4j || echo "Neo4j 已停止"

echo ">>> 所有组件已关闭!"