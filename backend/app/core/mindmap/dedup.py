"""思维导图题目去重逻辑"""

import re
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.mindmap import MindMapNode
from app.models.question import Question

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """标准化文本：去除空白字符、统一标点"""
    text = re.sub(r'\s+', '', text)
    text = text.replace('．', '.').replace('，', ',').replace('：', ':')
    text = text.replace('（', '(').replace('）', ')')
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    return text.lower()


async def check_duplicate_question(
    db: AsyncSession,
    content: str,
    mindmap_id: uuid.UUID,
) -> tuple[bool, Question | None]:
    """
    检查题目是否已存在于指定思维导图中。
    策略：精确匹配 content 字段（去除空白和标点差异后比较）
    """
    # 获取该思维导图关联的所有模块ID
    nodes_result = await db.execute(
        select(MindMapNode.module_id).where(
            MindMapNode.mind_map_id == mindmap_id,
            MindMapNode.module_id.isnot(None),
        )
    )
    module_ids = [row[0] for row in nodes_result.all()]

    if not module_ids:
        return False, None

    # 标准化题目文本用于比较
    normalized = normalize_text(content)

    existing_result = await db.execute(
        select(Question).where(
            Question.module_id.in_(module_ids),
            Question.is_valid == True,
        )
    )
    for q in existing_result.scalars().all():
        if normalize_text(q.content) == normalized:
            logger.info(f"发现重复题目: {content[:50]}...")
            return True, q

    return False, None


async def check_duplicate_batch(
    db: AsyncSession,
    contents: list[str],
    mindmap_id: uuid.UUID,
) -> dict[int, Question | None]:
    """
    批量检查题目是否重复。
    返回: {索引: 已存在的Question或None}
    """
    nodes_result = await db.execute(
        select(MindMapNode.module_id).where(
            MindMapNode.mind_map_id == mindmap_id,
            MindMapNode.module_id.isnot(None),
        )
    )
    module_ids = [row[0] for row in nodes_result.all()]

    if not module_ids:
        return {i: None for i in range(len(contents))}

    existing_result = await db.execute(
        select(Question).where(
            Question.module_id.in_(module_ids),
            Question.is_valid == True,
        )
    )
    existing_questions = existing_result.scalars().all()

    normalized_existing = {normalize_text(q.content): q for q in existing_questions}

    result: dict[int, Question | None] = {}
    for i, content in enumerate(contents):
        normalized = normalize_text(content)
        result[i] = normalized_existing.get(normalized)

    return result
