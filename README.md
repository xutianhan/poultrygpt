# poultrygpt-middleware
FastAPI 实现的轻量级中间件，支持 Redis 诊断多轮会话 ⇄ Neo4j 知识图谱家禽疾病诊断。

# code structure
poultrygpt-middleware/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 环境变量 & 配置
│   ├── api/
│   │   └── chat.py        # 与Dify交互的接口实现
│   ├── services/
│   │   ├── redis_service.py  # 会话状态管理
│   │   └── neo4j_service.py  # 诊断路径查询
│   └── models/
│       └── chat.py        # 与Dify交互的接口参数定义
├── run.sh     # 一键启动中间件服务（StenceTransformer实体相似度模型 + Neo4j + Redis）脚本
├── stop.sh     # 一键关闭中间件服务脚本
├── requirements.txt
└── README.md