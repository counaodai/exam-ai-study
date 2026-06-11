import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.mindmap import MindMap, MindMapNode
from app.models.module import Module
from app.models.question import Question

logger = logging.getLogger(__name__)

METHOD_GENERATION_THRESHOLD = 5


async def find_or_create_mindmap(
    db: AsyncSession,
    primary_module: str,
) -> MindMap:
    result = await db.execute(
        select(MindMap).where(MindMap.root_module == primary_module)
    )
    mindmap = result.scalar_one_or_none()

    if not mindmap:
        mindmap = MindMap(
            title=f"{primary_module}知识体系",
            root_module=primary_module,
        )
        db.add(mindmap)
        await db.flush()

        root_node = MindMapNode(
            mind_map_id=mindmap.id,
            label=primary_module,
            type="module",
            is_auto_generated=True,
            position_x=400,
            position_y=100,
        )
        db.add(root_node)
        await db.flush()
        logger.info(f"创建新思维导图: {primary_module}")

    return mindmap


async def find_module_id_by_name(
    db: AsyncSession,
    module_name: str,
    parent_name: str | None = None,
) -> uuid.UUID | None:
    query = select(Module).where(Module.name == module_name)

    if parent_name:
        parent_query = select(Module).where(Module.name == parent_name)
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()
        if parent:
            query = query.where(Module.parent_id == parent.id)

    result = await db.execute(query)
    module = result.scalar_one_or_none()
    return module.id if module else None


async def find_or_create_topic_node(
    db: AsyncSession,
    mindmap: MindMap,
    secondary_module: str,
    primary_module: str,
) -> MindMapNode:
    nodes_result = await db.execute(
        select(MindMapNode).where(MindMapNode.mind_map_id == mindmap.id)
    )
    all_nodes = nodes_result.scalars().all()

    root_node = None
    for node in all_nodes:
        if node.type == "module" and node.parent_id is None:
            root_node = node
            break

    for node in all_nodes:
        if node.label == secondary_module and node.type == "topic":
            return node

    if not root_node:
        root_node = MindMapNode(
            mind_map_id=mindmap.id,
            label=primary_module,
            type="module",
            is_auto_generated=True,
            position_x=400,
            position_y=100,
        )
        db.add(root_node)
        await db.flush()

    existing_topics = [n for n in all_nodes if n.parent_id == root_node.id]
    topic_count = len(existing_topics)

    new_node = MindMapNode(
        mind_map_id=mindmap.id,
        parent_id=root_node.id,
        label=secondary_module,
        type="topic",
        is_auto_generated=True,
        position_x=200 + topic_count * 200,
        position_y=250,
    )
    db.add(new_node)
    await db.flush()
    logger.info(f"创建新主题节点: {secondary_module}")
    return new_node


async def get_node_level(db: AsyncSession, node: MindMapNode) -> int:
    level = 0
    current = node
    while current.parent_id:
        level += 1
        parent_result = await db.execute(
            select(MindMapNode).where(MindMapNode.id == current.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            break
        current = parent
    return level


async def update_mindmap_after_classification(
    db: AsyncSession,
    primary_module: str,
    secondary_module: str | None,
    question_id: uuid.UUID | None = None,
) -> dict:
    mindmap = await find_or_create_mindmap(db, primary_module)

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
        logger.warning("未找到目标节点")
        return {"updated": False, "reason": "未找到目标节点"}

    target_node.question_count += 1

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
            mastery = min(int((total_questions / 20) * 100), 100)
            target_node.mastery = mastery

    should_generate_method = target_node.question_count >= METHOD_GENERATION_THRESHOLD

    await db.flush()

    node_level = await get_node_level(db, target_node)

    logger.info(
        f"思维导图更新完成: {primary_module} > {secondary_module or '根节点'}, "
        f"题目数: {target_node.question_count}, 掌握度: {target_node.mastery}"
    )

    return {
        "updated": True,
        "mindmap_id": str(mindmap.id),
        "node_id": str(target_node.id),
        "node_label": target_node.label,
        "node_level": node_level,
        "question_count": target_node.question_count,
        "mastery": target_node.mastery,
        "should_generate_method": should_generate_method,
    }
