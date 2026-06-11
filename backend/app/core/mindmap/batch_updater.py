"""思维导图批量更新器 — 支持多道题目批量导入到导图"""

import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.mindmap import MindMap, MindMapNode
from app.models.question import Question
from app.core.mindmap.updater import (
    find_or_create_mindmap,
    find_or_create_topic_node,
    find_module_id_by_name,
    get_node_level,
)

logger = logging.getLogger(__name__)

METHOD_GENERATION_THRESHOLD = 5


async def batch_update_mindmap(
    db: AsyncSession,
    mindmap_id: uuid.UUID,
    questions_data: list[dict],
) -> dict:
    """
    批量更新思维导图：为多道题目更新对应节点的计数和掌握度。

    questions_data: [{"primary_module": str, "secondary_module": str | None, "question_id": uuid.UUID}, ...]

    返回: {
        "updated_nodes": [{node_id, node_label, question_count, mastery, ...}],
        "should_generate_methods": [node_id, ...],
    }
    """
    mindmap = await db.get(MindMap, mindmap_id)
    if not mindmap:
        raise ValueError(f"思维导图不存在: {mindmap_id}")

    # 按 (primary_module, secondary_module) 分组
    from collections import defaultdict
    groups: dict[tuple[str, str | None], list[uuid.UUID]] = defaultdict(list)

    for qd in questions_data:
        key = (qd["primary_module"], qd.get("secondary_module"))
        groups[key].append(qd["question_id"])

    updated_nodes = []
    should_generate_methods = []

    for (primary_module, secondary_module), question_ids in groups.items():
        target_node = None

        if secondary_module:
            target_node = await find_or_create_topic_node(
                db, mindmap, secondary_module, primary_module
            )
        else:
            nodes_result = await db.execute(
                select(MindMapNode).where(
                    MindMapNode.mind_map_id == mindmap.id,
                    MindMapNode.type == "module",
                    MindMapNode.parent_id.is_(None),
                )
            )
            target_node = nodes_result.scalar_one_or_none()

        if not target_node:
            logger.warning(f"未找到目标节点: {primary_module} > {secondary_module}")
            continue

        count = len(question_ids)
        target_node.question_count += count

        # 重新计算掌握度
        module_id = await find_module_id_by_name(
            db,
            secondary_module or primary_module,
            primary_module if secondary_module else None,
        )

        if module_id:
            count_result = await db.execute(
                select(func.count(Question.id)).where(
                    Question.module_id == module_id,
                    Question.is_valid == True,
                )
            )
            total_questions = count_result.scalar() or 0
            if total_questions > 0:
                target_node.mastery = min(int((total_questions / 20) * 100), 100)

        node_level = await get_node_level(db, target_node)

        updated_nodes.append({
            "node_id": str(target_node.id),
            "node_label": target_node.label,
            "node_level": node_level,
            "question_count": target_node.question_count,
            "mastery": target_node.mastery,
        })

        if target_node.question_count >= METHOD_GENERATION_THRESHOLD:
            should_generate_methods.append(str(target_node.id))

    await db.flush()

    logger.info(f"批量更新思维导图完成: 更新了 {len(updated_nodes)} 个节点")

    return {
        "updated_nodes": updated_nodes,
        "should_generate_methods": should_generate_methods,
    }
