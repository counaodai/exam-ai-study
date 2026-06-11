import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.ai.classifier import classify_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/classify", tags=["题目分类"])


class ClassifyRequest(BaseModel):
    question_text: str


class ClassifyResponse(BaseModel):
    primary_module: str
    secondary_module: str | None = None
    tertiary_module: str | None = None
    confidence: float
    method: str
    reason: str


@router.post("", response_model=ClassifyResponse)
async def classify(request: ClassifyRequest):
    result = await classify_question(request.question_text)
    return ClassifyResponse(
        primary_module=result.primary_module,
        secondary_module=result.secondary_module,
        tertiary_module=result.tertiary_module,
        confidence=result.confidence,
        method=result.method,
        reason=result.reason,
    )
