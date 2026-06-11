"""题目导入 API — 解析粘贴文本、批量导入到思维导图"""

import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.database import get_db
from app.models.question import Question
from app.models.module import Module
from app.models.mindmap import MindMap, MindMapNode
from app.schemas.question_import import (
    ParseQuestionsRequest,
    ParseQuestionsResponse,
    ImportQuestionsRequest,
    ImportQuestionsResponse,
    QuestionListResponse,
    QuestionListItem,
    CheckDuplicateRequest,
    CheckDuplicateResponse,
)
from app.core.ai.question_parser import parse_questions
from app.core.ai.content_filter import validate_question_content, sanitize_text, validate_batch_size
from app.core.mindmap.dedup import check_duplicate_question
from app.core.mindmap.batch_updater import batch_update_mindmap
from app.core.ai.classifier import classify_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["题目导入"])


# ===== 模块A：自主选择导入 =====

@router.get("", response_model=QuestionListResponse)
async def get_questions_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    module_id: str | None = Query(None, description="按模块筛选"),
    keyword: str | None = Query(None, description="按关键词搜索"),
    is_valid: bool | None = Query(None, description="按有效性筛选"),
    db: AsyncSession = Depends(get_db),
):
    """获取所有已生成的题目列表（支持分页、按模块筛选、关键词搜索）"""
    query = select(Question)

    if module_id:
        query = query.where(Question.module_id == uuid.UUID(module_id))
    if is_valid is not None:
        query = query.where(Question.is_valid == is_valid)
    if keyword:
        query = query.where(Question.content.ilike(f"%{keyword}%"))

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分页
    items_result = await db.execute(
        query.order_by(Question.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    questions = items_result.scalars().all()

    # 批量获取模块信息
    module_ids = [q.module_id for q in questions if q.module_id]
    module_map: dict[uuid.UUID, Module] = {}
    if module_ids:
        modules_result = await db.execute(
            select(Module).where(Module.id.in_(module_ids))
        )
        for m in modules_result.scalars().all():
            module_map[m.id] = m

    items = []
    for q in questions:
        module = module_map.get(q.module_id) if q.module_id else None
        module_path = None
        if module:
            path_parts = [module.name]
            current = module
            while current.parent_id:
                parent_result = await db.execute(
                    select(Module).where(Module.id == current.parent_id)
                )
                parent = parent_result.scalar_one_or_none()
                if parent:
                    path_parts.insert(0, parent.name)
                    current = parent
                else:
                    break
            module_path = " > ".join(path_parts)

        items.append(QuestionListItem(
            id=str(q.id),
            content=q.content,
            answer=q.answer,
            explanation=q.explanation,
            source=q.source,
            module_id=str(q.module_id) if q.module_id else None,
            module_name=module.name if module else None,
            module_path=module_path,
            difficulty=q.difficulty,
            mastery=q.mastery,
            is_valid=q.is_valid,
            created_at=q.created_at,
        ))

    return QuestionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/check-duplicate", response_model=CheckDuplicateResponse)
async def check_duplicate(
    request: CheckDuplicateRequest,
    db: AsyncSession = Depends(get_db),
):
    """检查题目是否已存在于指定思维导图中"""
    is_dup, existing = await check_duplicate_question(
        db, request.content, uuid.UUID(request.mindmap_id)
    )
    return CheckDuplicateResponse(
        is_duplicate=is_dup,
        existing_question_id=str(existing.id) if existing else None,
        existing_question_content=existing.content[:100] if existing else None,
    )


# ===== 模块B：复制导入 =====

@router.post("/parse", response_model=ParseQuestionsResponse)
async def parse_question_text(
    request: ParseQuestionsRequest,
    db: AsyncSession = Depends(get_db),
):
    """解析粘贴的题目文本，识别题目结构"""
    # 内容审核
    sanitized = sanitize_text(request.content)
    if not sanitized:
        return ParseQuestionsResponse(questions=[], parse_errors=[{
            "error": "内容为空",
            "message": "请粘贴题目内容后再识别",
        }])

    if len(sanitized) > 10000:
        return ParseQuestionsResponse(questions=[], parse_errors=[{
            "error": "内容过长",
            "message": "粘贴内容过长，建议分批导入（当前支持单次最多10道题目）",
        }])

    # 敏感内容检查
    is_valid, reason = validate_question_content(sanitized)
    if not is_valid:
        return ParseQuestionsResponse(questions=[], parse_errors=[{
            "error": "内容违规",
            "message": reason,
        }])

    # 解析题目
    questions, errors = await parse_questions(sanitized, request.format)

    # 为每道解析成功的题目进行自动分类
    for q in questions:
        try:
            classification = await classify_question(q.content)
            if classification and classification.primary_module != "未分类":
                q.suggested_module_path = classification.primary_module
                if classification.secondary_module:
                    q.suggested_module_path += f" > {classification.secondary_module}"
        except Exception as e:
            logger.warning(f"自动分类失败: {e}")

    return ParseQuestionsResponse(
        questions=questions,
        parse_errors=errors,
    )


@router.post("/import-parsed", response_model=ImportQuestionsResponse)
async def import_parsed_questions(
    request: ImportQuestionsRequest,
    db: AsyncSession = Depends(get_db),
):
    """将解析后的题目批量创建并导入思维导图"""
    # 验证批量数量
    is_valid, reason = validate_batch_size(len(request.questions))
    if not is_valid:
        raise HTTPException(status_code=400, detail=reason)

    imported_ids = []
    failed = []
    questions_data_for_mindmap = []

    for i, item in enumerate(request.questions):
        try:
            # 内容审核
            sanitized = sanitize_text(item.content)
            is_valid_content, reason = validate_question_content(sanitized)
            if not is_valid_content:
                failed.append({
                    "index": i,
                    "content_preview": item.content[:50],
                    "reason": reason,
                })
                continue

            # 确定模块ID
            module_id = None
            primary_module = ""
            secondary_module = item.secondary_module

            if item.module_id:
                module_id = uuid.UUID(item.module_id)
                # 查询模块信息
                module = await db.get(Module, module_id)
                if module:
                    primary_module = module.name
                    # 查找一级模块
                    current = module
                    while current.parent_id:
                        parent_result = await db.execute(
                            select(Module).where(Module.id == current.parent_id)
                        )
                        parent = parent_result.scalar_one_or_none()
                        if parent:
                            primary_module = parent.name
                            current = parent
                        else:
                            break
            else:
                # 自动分类
                try:
                    classification = await classify_question(sanitized)
                    if classification and classification.primary_module != "未分类":
                        primary_module = classification.primary_module
                        secondary_module = secondary_module or classification.secondary_module
                except Exception as e:
                    logger.warning(f"自动分类失败: {e}")

            if not primary_module:
                failed.append({
                    "index": i,
                    "content_preview": item.content[:50],
                    "reason": "无法确定题目分类",
                })
                continue

            # 查找模块ID
            if not module_id:
                module_query = select(Module).where(Module.name == (secondary_module or primary_module))
                if secondary_module:
                    parent_query = select(Module).where(Module.name == primary_module)
                    parent_result = await db.execute(parent_query)
                    parent = parent_result.scalar_one_or_none()
                    if parent:
                        module_query = module_query.where(Module.parent_id == parent.id)
                module_result = await db.execute(module_query)
                module = module_result.scalar_one_or_none()
                if module:
                    module_id = module.id

            # 创建Question记录
            question = Question(
                content=sanitized,
                options=item.options,
                answer=item.answer,
                explanation=item.explanation,
                module_id=module_id,
                source="粘贴导入",
                mastery=0,
            )
            db.add(question)
            await db.flush()

            imported_ids.append(str(question.id))
            questions_data_for_mindmap.append({
                "primary_module": primary_module,
                "secondary_module": secondary_module,
                "question_id": question.id,
            })

        except Exception as e:
            logger.error(f"导入题目失败: {e}")
            failed.append({
                "index": i,
                "content_preview": item.content[:50],
                "reason": str(e),
            })

    await db.commit()

    return ImportQuestionsResponse(
        imported_count=len(imported_ids),
        imported_ids=imported_ids,
        failed=failed,
        mindmap_update=None,
    )
