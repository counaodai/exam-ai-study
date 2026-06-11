from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path, override=True)

from pydantic_settings import BaseSettings
from typing import List
import json
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # MySQL 数据库配置
    DATABASE_URL: str = "mysql+aiomysql://root:2004@localhost:3306/exam_study"

    # LLM 配置（OpenAI 兼容接口，复用 OPENAI_API_KEY 和 OPENAI_BASE_URL）
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "deepseek-ai/DeepSeek-V4-Pro"

    # 保留 OpenAI 配置（用于 Embedding 等）
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Rerank 重排序配置（复用 OPENAI_API_KEY 和 OPENAI_BASE_URL）
    RERANK_ENABLED: bool = True
    RERANK_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANK_TOP_K: int = 10  # 向量检索返回的候选数（粗排数量）
    RERANK_TOP_N: int = 3   # Rerank 后保留的文档数（精排数量）

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50

    APP_ENV: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> List[str]:
        try:
            origins = json.loads(self.CORS_ORIGINS)
            if isinstance(origins, list):
                return origins
        except (json.JSONDecodeError, TypeError):
            pass
        if "," in self.CORS_ORIGINS:
            return [o.strip().strip("'\"") for o in self.CORS_ORIGINS.split(",")]
        return ["http://localhost:5173"]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
logger.info(f"CORS 允许的源: {settings.cors_origins_list}")
