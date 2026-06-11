from contextlib import asynccontextmanager
import logging
import traceback
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.db.database import init_db, get_db
from app.db.init_data import init_preset_modules
from app.api import (
    documents_router,
    chat_router,
    mindmaps_router,
    analysis_router,
    methods_router,
    modules_router,
    classify_router,
    cleanup_router,
    questions_router,
)

logger = logging.getLogger(__name__)


class CORSErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"未捕获的异常: {exc}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"服务器内部错误: {str(exc)}"},
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.warning(f"数据库连接失败，请检查数据库配置: {e}")
        logger.warning("应用将继续启动，但数据库相关功能将不可用")
    yield


app = FastAPI(
    title="公考AI智能学习系统",
    description="基于 RAG 知识库的公考智能学习助手",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(mindmaps_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(methods_router, prefix="/api")
app.include_router(modules_router, prefix="/api")
app.include_router(classify_router, prefix="/api")
app.include_router(cleanup_router, prefix="/api")
app.include_router(questions_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/init-preset-data")
async def init_preset_data(db: AsyncSession = Depends(get_db)):
    """初始化预置公考模块数据"""
    try:
        from app.models.module import Module
        from sqlalchemy import select

        result = await db.execute(select(Module).where(Module.is_preset == True))
        existing = result.scalars().first()
        if existing:
            return {"message": "预置数据已存在，跳过初始化", "already_exists": True}

        await init_preset_modules(db)
        return {"message": "预置数据初始化成功", "already_exists": False}
    except Exception as e:
        logger.error(f"初始化预置数据失败: {e}")
        return {"detail": f"初始化预置数据失败: {str(e)}"}
