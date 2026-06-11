"""
数据清理 API — 清理历史误统计的无效提问数据
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text
from pydantic import BaseModel

from app.db.database import get_db
from app.models.question import Question
from app.models.conversation import Message
from app.models.mindmap import MindMapNode
from app.core.ai.question_validator import check_by_keyword_rules

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cleanup", tags=["数据清理"])


class CleanupResult(BaseModel):
    """清理结果"""
    total_questions_scanned: int
    invalid_questions_found: int
    invalid_questions_cleaned: int
    mindmap_nodes_updated: int
    details: list[dict] = []


@router.post("/invalid-questions", response_model=CleanupResult)
async def cleanup_invalid_questions(db: AsyncSession = Depends(get_db)):
    """
    批量清理历史无效提问数据：
    1. 扫描所有 Question 记录，用关键词规则检测无效提问
    2. 将无效提问标记为 is_valid=False
    3. 修正对应思维导图节点的 question_count 和 mastery
    """
    # 查询所有标记为有效的 Question
    result = await db.execute(
        select(Question).where(Question.is_valid == True)
    )
    all_questions = result.scalars().all()

    total_scanned = len(all_questions)
    invalid_ids = []
    details = []

    # 用关键词规则扫描
    for q in all_questions:
        is_invalid, reason = check_by_keyword_rules(q.content)
        if is_invalid:
            invalid_ids.append(q.id)
            details.append({
                "question_id": str(q.id),
                "content": q.content[:80],
                "reason": reason,
                "module_id": str(q.module_id) if q.module_id else None,
            })

    # 批量标记无效
    cleaned_count = 0
    if invalid_ids:
        await db.execute(
            update(Question)
            .where(Question.id.in_(invalid_ids))
            .values(is_valid=False)
        )
        cleaned_count = len(invalid_ids)

    # 修正思维导图节点统计
    nodes_updated = 0
    if invalid_ids:
        # 获取受影响的 module_id 列表
        affected_modules_result = await db.execute(
            select(Question.module_id, func.count(Question.id))
            .where(Question.id.in_(invalid_ids))
            .group_by(Question.module_id)
        )
        affected_modules = affected_modules_result.all()

        for module_id, invalid_count in affected_modules:
            if not module_id:
                continue

            # 更新对应思维导图节点
            node_result = await db.execute(
                select(MindMapNode).where(MindMapNode.module_id == module_id)
            )
            nodes = node_result.scalars().all()

            for node in nodes:
                # 重新计算该模块下的有效题目数
                valid_count_result = await db.execute(
                    select(func.count(Question.id))
                    .where(
                        Question.module_id == module_id,
                        Question.is_valid == True,
                    )
                )
                valid_count = valid_count_result.scalar() or 0

                node.question_count = max(0, valid_count)
                if valid_count > 0:
                    node.mastery = min(int((valid_count / 20) * 100), 100)
                else:
                    node.mastery = 0
                nodes_updated += 1

    await db.commit()

    logger.info(
        f"数据清理完成: 扫描 {total_scanned} 条, "
        f"发现无效 {cleaned_count} 条, "
        f"更新节点 {nodes_updated} 个"
    )

    return CleanupResult(
        total_questions_scanned=total_scanned,
        invalid_questions_found=cleaned_count,
        invalid_questions_cleaned=cleaned_count,
        mindmap_nodes_updated=nodes_updated,
        details=details[:50],  # 最多返回50条详情
    )


@router.get("/invalid-stats")
async def get_invalid_stats(db: AsyncSession = Depends(get_db)):
    """获取无效提问统计信息"""
    total = await db.scalar(select(func.count(Question.id)))
    valid = await db.scalar(
        select(func.count(Question.id)).where(Question.is_valid == True)
    )
    invalid = await db.scalar(
        select(func.count(Question.id)).where(Question.is_valid == False)
    )

    # 获取无效提问示例
    invalid_samples_result = await db.execute(
        select(Question.content)
        .where(Question.is_valid == False)
        .limit(10)
    )
    invalid_samples = [row[0][:100] for row in invalid_samples_result.all()]

    return {
        "total_questions": total or 0,
        "valid_questions": valid or 0,
        "invalid_questions": invalid or 0,
        "invalid_samples": invalid_samples,
    }
