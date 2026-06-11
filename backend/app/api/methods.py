import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.method import MethodSummary
from app.models.module import Module
from app.models.question import Question
from app.schemas.method import (
    MethodSummaryResponse,
    GenerateMethodRequest,
    UpdateMethodRequest,
    MethodRecognition,
    MethodStep,
    MethodTrap,
)
from app.core.ai.method_extract import extract_method

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/methods", tags=["方法论"])


def _build_method_response(method: MethodSummary) -> MethodSummaryResponse:
    recognition = None
    if method.recognition:
        recognition = MethodRecognition(**method.recognition)

    steps = []
    if method.steps:
        steps = [MethodStep(**s) if isinstance(s, dict) else s for s in method.steps]

    traps = []
    if method.traps:
        traps = [MethodTrap(**t) if isinstance(t, dict) else t for t in method.traps]

    return MethodSummaryResponse(
        id=str(method.id),
        module_id=str(method.module_id) if method.module_id else None,
        method_name=method.method_name,
        recognition=recognition,
        steps=steps,
        traps=traps,
        quick_tips=method.quick_tips or [],
        key_formulas=method.key_formulas or [],
        summary=method.summary,
        question_count=method.question_count,
        source_question_ids=[str(qid) for qid in (method.source_question_ids or [])],
        is_auto_generated=method.is_auto_generated,
        created_at=method.created_at,
        updated_at=method.updated_at,
    )


@router.get("", response_model=list[MethodSummaryResponse])
async def get_method_list(
    module_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(MethodSummary).order_by(MethodSummary.created_at.desc())
    if module_id:
        query = query.where(MethodSummary.module_id == uuid.UUID(module_id))
    result = await db.execute(query)
    methods = result.scalars().all()
    return [_build_method_response(m) for m in methods]


@router.get("/{method_id}", response_model=MethodSummaryResponse)
async def get_method_detail(method_id: str, db: AsyncSession = Depends(get_db)):
    method = await db.get(MethodSummary, uuid.UUID(method_id))
    if not method:
        raise HTTPException(status_code=404, detail="方法论不存在")
    return _build_method_response(method)


@router.post("/generate", response_model=MethodSummaryResponse)
async def generate_method(
    request: GenerateMethodRequest,
    db: AsyncSession = Depends(get_db),
):
    module = await db.get(Module, uuid.UUID(request.module_id))
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")

    existing = await db.execute(
        select(MethodSummary).where(MethodSummary.module_id == module.id)
    )
    existing_method = existing.scalar_one_or_none()
    if existing_method:
        return _build_method_response(existing_method)

    module_name = module.name
    parent_name = None
    if module.parent_id:
        parent = await db.get(Module, module.parent_id)
        if parent:
            parent_name = parent.name
            module_name = f"{parent.name} > {module.name}"

    question_query = (
        select(Question)
        .where(Question.module_id == module.id)
        .order_by(Question.created_at.desc())
        .limit(20)
    )
    q_result = await db.execute(question_query)
    questions = q_result.scalars().all()

    if not questions:
        raise HTTPException(status_code=400, detail="该模块下没有题目，无法生成方法论")

    questions_data = [
        {
            "content": q.content,
            "answer": q.answer or "",
            "explanation": q.explanation or "",
        }
        for q in questions
    ]

    try:
        method_result = await extract_method(module_name, questions_data)
    except Exception as e:
        logger.error(f"方法论生成失败: {e}")
        raise HTTPException(status_code=500, detail="方法论生成失败，请稍后重试")

    source_ids = [str(q.id) for q in questions]

    method = MethodSummary(
        module_id=module.id,
        method_name=method_result.get("method_name", f"{module.name}解题方法"),
        recognition=method_result.get("recognition"),
        steps=method_result.get("steps", []),
        traps=method_result.get("traps"),
        quick_tips=method_result.get("quick_tips"),
        key_formulas=method_result.get("key_formulas"),
        summary=method_result.get("summary"),
        question_count=len(questions),
        source_question_ids=source_ids,
        is_auto_generated=True,
    )
    db.add(method)
    await db.commit()
    await db.refresh(method)

    logger.info(f"方法论生成成功: {method.method_name}, 模块: {module_name}")
    return _build_method_response(method)


@router.put("/{method_id}", response_model=MethodSummaryResponse)
async def update_method(
    method_id: str,
    request: UpdateMethodRequest,
    db: AsyncSession = Depends(get_db),
):
    method = await db.get(MethodSummary, uuid.UUID(method_id))
    if not method:
        raise HTTPException(status_code=404, detail="方法论不存在")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "recognition" and value is not None:
            value = value if isinstance(value, dict) else value.model_dump()
        elif field == "steps" and value is not None:
            value = [s if isinstance(s, dict) else s.model_dump() for s in value]
        elif field == "traps" and value is not None:
            value = [t if isinstance(t, dict) else t.model_dump() for t in value]
        setattr(method, field, value)

    method.is_auto_generated = False
    await db.commit()
    await db.refresh(method)
    return _build_method_response(method)


async def generate_method_for_module(
    db: AsyncSession,
    module_id: uuid.UUID,
) -> MethodSummary | None:
    existing = await db.execute(
        select(MethodSummary).where(MethodSummary.module_id == module_id)
    )
    if existing.scalar_one_or_none():
        return None

    module = await db.get(Module, module_id)
    if not module:
        return None

    module_name = module.name
    if module.parent_id:
        parent = await db.get(Module, module.parent_id)
        if parent:
            module_name = f"{parent.name} > {module.name}"

    question_query = (
        select(Question)
        .where(Question.module_id == module.id)
        .order_by(Question.created_at.desc())
        .limit(20)
    )
    q_result = await db.execute(question_query)
    questions = q_result.scalars().all()

    if len(questions) < 3:
        return None

    questions_data = [
        {
            "content": q.content,
            "answer": q.answer or "",
            "explanation": q.explanation or "",
        }
        for q in questions
    ]

    try:
        method_result = await extract_method(module_name, questions_data)
    except Exception as e:
        logger.error(f"自动方法论生成失败: {e}")
        return None

    source_ids = [str(q.id) for q in questions]

    method = MethodSummary(
        module_id=module.id,
        method_name=method_result.get("method_name", f"{module.name}解题方法"),
        recognition=method_result.get("recognition"),
        steps=method_result.get("steps", []),
        traps=method_result.get("traps"),
        quick_tips=method_result.get("quick_tips"),
        key_formulas=method_result.get("key_formulas"),
        summary=method_result.get("summary"),
        question_count=len(questions),
        source_question_ids=source_ids,
        is_auto_generated=True,
    )
    db.add(method)
    await db.flush()

    logger.info(f"自动方法论生成成功: {method.method_name}")
    return method
