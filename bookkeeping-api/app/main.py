"""FastAPI 应用装配：中间件、路由、异常处理与 Swagger 文档。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accounts, auth, categories, stats, transactions, users
from app.core.config import get_settings
from app.core.errors import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title="个人记账管理系统 API",
    description=(
        "基于 FastAPI + SQLAlchemy 2.0 + MySQL 8.0 的记账后端。"
        "所有成功响应统一为 {code, message, data} 信封结构；"
        "交互式文档见 /docs。"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for api_router in (
    auth.router,
    users.router,
    accounts.router,
    categories.router,
    transactions.router,
    stats.router,
):
    app.include_router(api_router, prefix="/api/v1")

register_exception_handlers(app)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok"}
