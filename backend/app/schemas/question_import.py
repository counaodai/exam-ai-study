"""题目导入相关的 Pydantic Schema"""

from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class ParsedQuestionItem(BaseModel):
    """解析后的单道题目"""
    content: str
    options: dict[str, str] | None = None
    answer: str | None = None
    explanation: str | None = None
    suggested_module_id: str | None = None
    suggested_module_path: str | None = None
    parse_confidence: float = 0.0


class ParseQuestionsRequest(BaseModel):
    """题目解析请求"""
    content: str
    format: str = "plain"  # plain | markdown


class ParseQuestionsResponse(BaseModel):
    """题目解析响应"""
    questions: list[ParsedQuestionItem]
    parse_errors: list[dict] = []


class ImportQuestionItem(BaseModel):
    """单道待导入题目"""
    content: str
    options: dict[str, str] | None = None
    answer: str | None = None
    explanation: str | None = None
    module_id: str | None = None
    secondary_module: str | None = None


class ImportQuestionsRequest(BaseModel):
    """批量导入请求"""
    questions: list[ImportQuestionItem]
    allow_duplicate: bool = False


class ImportQuestionsResponse(BaseModel):
    """批量导入响应"""
    imported_count: int
    imported_ids: list[str]
    failed: list[dict]
    mindmap_update: dict | None = None


class QuestionListItem(BaseModel):
    """题目列表项"""
    id: str
    content: str
    answer: str | None = None
    explanation: str | None = None
    source: str | None = None
    module_id: str | None = None
    module_name: str | None = None
    module_path: str | None = None
    difficulty: int | None = None
    mastery: int = 0
    is_valid: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionListResponse(BaseModel):
    """题目列表响应"""
    items: list[QuestionListItem]
    total: int
    page: int
    page_size: int


class CheckDuplicateRequest(BaseModel):
    """去重检查请求"""
    content: str
    mindmap_id: str


class CheckDuplicateResponse(BaseModel):
    """去重检查响应"""
    is_duplicate: bool
    existing_question_id: str | None = None
    existing_question_content: str | None = None


class ImportProgressItem(BaseModel):
    """单道题目导入进度"""
    content_preview: str
    status: str  # pending | success | failed
    question_id: str | None = None
    error: str | None = None


class ImportProgressResponse(BaseModel):
    """导入进度响应"""
    task_id: str
    total: int
    completed: int
    status: str  # pending | processing | completed | failed
    results: list[ImportProgressItem] = []
