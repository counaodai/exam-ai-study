from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.db.database import get_db
from app.models.mindmap import MindMap, MindMapNode, MindMapEdge
from app.models.method import MethodSummary
from app.models.question import Question
from app.models.module import Module
from app.schemas.mindmap import (
    MindMapResponse,
    MindMapNodeResponse,
    MindMapEdge as MindMapEdgeSchema,
    NodeMetadata,
    CreateMindMapRequest,
    UpdateNodeRequest,
    CreateNodeRequest,
    CreateNodeResponseData,
    CreateEdgeRequest,
    UpdateEdgeRequest,
    DeleteNodeResponse,
    NodeQuestionsResponse,
    NodeQuestionItem,
)
from app.schemas.question_import import (
    ImportQuestionsRequest,
    ImportQuestionsResponse,
)
from app.core.mindmap.dedup import check_duplicate_question
from app.core.mindmap.batch_updater import batch_update_mindmap
from app.core.ai.content_filter import validate_question_content, sanitize_text
from app.core.ai.classifier import classify_question
import uuid

router = APIRouter(prefix="/mindmaps", tags=["思维导图"])


async def _build_mindmap_response(m: MindMap, db: AsyncSession) -> MindMapResponse:
    nodes_result = await db.execute(
        select(MindMapNode).where(MindMapNode.mind_map_id == m.id)
    )
    nodes = nodes_result.scalars().all()

    module_ids = [n.module_id for n in nodes if n.module_id]
    method_map: dict[str, str] = {}
    if module_ids:
        methods_result = await db.execute(
            select(MethodSummary).where(MethodSummary.module_id.in_(module_ids))
        )
        for method in methods_result.scalars().all():
            method_map[str(method.module_id)] = str(method.id)

    # 读取已持久化的边
    edges_result = await db.execute(
        select(MindMapEdge).where(MindMapEdge.mind_map_id == m.id)
    )
    persisted_edges = list(edges_result.scalars().all())

    edges: list[MindMapEdgeSchema] = []
    for e in persisted_edges:
        edges.append(MindMapEdgeSchema(
            id=str(e.id),
            source=str(e.source_id),
            target=str(e.target_id),
            edge_type=e.edge_type,
            color=e.color,
            stroke_width=e.stroke_width,
            has_arrow=e.has_arrow,
            animated=e.animated,
            label=e.label,
            is_derived=e.is_derived,
        ))

    node_responses = []
    for node in nodes:
        method_id = method_map.get(str(node.module_id)) if node.module_id else None
        metadata = NodeMetadata(
            is_auto_generated=node.is_auto_generated,
            method_summary=method_id,
        )
        node_responses.append(MindMapNodeResponse(
            id=str(node.id),
            label=node.label,
            type=node.type,
            parent_id=str(node.parent_id) if node.parent_id else None,
            question_count=node.question_count,
            mastery=node.mastery,
            content=node.content,
            metadata=metadata,
            position={"x": node.position_x, "y": node.position_y},
        ))

    return MindMapResponse(
        id=str(m.id),
        title=m.title,
        root_module=m.root_module,
        nodes=node_responses,
        edges=edges,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.get("", response_model=list[MindMapResponse])
async def get_mindmap_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MindMap).order_by(MindMap.updated_at.desc()))
    maps = result.scalars().all()
    response = []
    for m in maps:
        response.append(await _build_mindmap_response(m, db))
    return response


@router.get("/{map_id}", response_model=MindMapResponse)
async def get_mindmap_detail(map_id: str, db: AsyncSession = Depends(get_db)):
    m = await db.get(MindMap, uuid.UUID(map_id))
    if not m:
        raise HTTPException(status_code=404, detail="思维导图不存在")
    return await _build_mindmap_response(m, db)


@router.post("", response_model=MindMapResponse)
async def create_mindmap(
    request: CreateMindMapRequest,
    db: AsyncSession = Depends(get_db),
):
    m = MindMap(title=request.title, root_module=request.root_module)
    db.add(m)
    await db.flush()

    root_node = MindMapNode(
        mind_map_id=m.id,
        label=request.root_module,
        type="module",
        position_x=400,
        position_y=100,
    )
    db.add(root_node)
    await db.flush()
    await db.refresh(m)

    return MindMapResponse(
        id=str(m.id),
        title=m.title,
        root_module=m.root_module,
        nodes=[MindMapNodeResponse(
            id=str(root_node.id),
            label=root_node.label,
            type=root_node.type,
            position={"x": root_node.position_x, "y": root_node.position_y},
        )],
        edges=[],
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.put("/{map_id}", response_model=MindMapResponse)
async def update_mindmap(
    map_id: str,
    request: CreateMindMapRequest,
    db: AsyncSession = Depends(get_db),
):
    m = await db.get(MindMap, uuid.UUID(map_id))
    if not m:
        raise HTTPException(status_code=404, detail="思维导图不存在")
    m.title = request.title
    await db.flush()
    await db.refresh(m)
    return await _build_mindmap_response(m, db)


@router.delete("/{map_id}")
async def delete_mindmap(map_id: str, db: AsyncSession = Depends(get_db)):
    m = await db.get(MindMap, uuid.UUID(map_id))
    if not m:
        raise HTTPException(status_code=404, detail="思维导图不存在")
    await db.delete(m)
    await db.flush()
    return {"message": "思维导图已删除"}


@router.put("/{map_id}/nodes/{node_id}")
async def update_node(
    map_id: str,
    node_id: str,
    request: UpdateNodeRequest,
    db: AsyncSession = Depends(get_db),
):
    node = await db.get(MindMapNode, uuid.UUID(node_id))
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    if request.label is not None:
        node.label = request.label
    if request.content is not None:
        node.content = request.content
    if request.position_x is not None:
        node.position_x = request.position_x
    if request.position_y is not None:
        node.position_y = request.position_y
    await db.flush()
    return {"message": "更新成功"}


@router.post("/{map_id}/nodes", response_model=CreateNodeResponseData)
async def add_node(
    map_id: str,
    request: CreateNodeRequest,
    db: AsyncSession = Depends(get_db),
):
    m = await db.get(MindMap, uuid.UUID(map_id))
    if not m:
        raise HTTPException(status_code=404, detail="思维导图不存在")

    parent_node = None
    if request.parent_id:
        parent_node = await db.get(MindMapNode, uuid.UUID(request.parent_id))
        if not parent_node:
            raise HTTPException(status_code=404, detail="父节点不存在")

    # 查询同一父节点下已有子节点数（通过 edges 表）
    siblings_count = 0
    if parent_node:
        siblings_result = await db.execute(
            select(func.count()).select_from(MindMapEdge).where(
                MindMapEdge.mind_map_id == m.id,
                MindMapEdge.source_id == parent_node.id,
            )
        )
        siblings_count = siblings_result.scalar() or 0

    parent_x = parent_node.position_x if parent_node else 400
    parent_y = parent_node.position_y if parent_node else 100

    new_node = MindMapNode(
        mind_map_id=m.id,
        parent_id=None,
        label=request.label,
        type=request.type,
        content=request.content,
        is_auto_generated=False,
        position_x=parent_x - 150 + siblings_count * 200,
        position_y=parent_y + 150,
    )
    db.add(new_node)
    await db.flush()

    created_edge = None
    if parent_node:
        edge = MindMapEdge(
            mind_map_id=m.id,
            source_id=parent_node.id,
            target_id=new_node.id,
            edge_type="default",
            color="#409EFF",
            stroke_width=2,
            has_arrow=True,
            animated=False,
            is_derived=True,
        )
        db.add(edge)
        await db.flush()
        created_edge = MindMapEdgeSchema(
            id=str(edge.id),
            source=str(edge.source_id),
            target=str(edge.target_id),
            edge_type=edge.edge_type,
            color=edge.color,
            stroke_width=edge.stroke_width,
            has_arrow=edge.has_arrow,
            animated=edge.animated,
            label=edge.label,
            is_derived=edge.is_derived,
        )

    return CreateNodeResponseData(
        node=MindMapNodeResponse(
            id=str(new_node.id),
            label=new_node.label,
            type=new_node.type,
            parent_id=str(new_node.parent_id) if new_node.parent_id else None,
            content=new_node.content,
            position={"x": new_node.position_x, "y": new_node.position_y},
        ),
        edge=created_edge,
    )


async def _delete_node_recursive(db: AsyncSession, node_id: uuid.UUID) -> int:
    # 通过 edges 查找子节点（edge.source→target 代表层级关系）
    children_result = await db.execute(
        select(MindMapNode).join(
            MindMapEdge,
            and_(MindMapEdge.target_id == MindMapNode.id, MindMapEdge.source_id == node_id),
        )
    )
    children = children_result.scalars().all()
    deleted_count = 0
    for child in children:
        deleted_count += await _delete_node_recursive(db, child.id)

    node = await db.get(MindMapNode, node_id)
    if node:
        # 删除以该节点为 source 或 target 的所有边
        await db.execute(
            MindMapEdge.__table__.delete().where(
                or_(MindMapEdge.source_id == node_id, MindMapEdge.target_id == node_id)
            )
        )
        await db.delete(node)
        deleted_count += 1
    return deleted_count


@router.delete("/{map_id}/nodes/{node_id}", response_model=DeleteNodeResponse)
async def delete_node(
    map_id: str,
    node_id: str,
    db: AsyncSession = Depends(get_db),
):
    node = await db.get(MindMapNode, uuid.UUID(node_id))
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    incoming_edge_result = await db.execute(
        select(MindMapEdge.id).where(
            MindMapEdge.mind_map_id == node.mind_map_id,
            MindMapEdge.target_id == node.id,
        )
    )
    if node.type == "module" and incoming_edge_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=400, detail="不允许删除根模块节点")

    deleted_count = await _delete_node_recursive(db, uuid.UUID(node_id))
    return DeleteNodeResponse(message="删除成功", deleted_count=deleted_count)


# ===== 边（连线）CRUD =====

async def _ensure_nodes_exist(db: AsyncSession, map_id: uuid.UUID, *node_ids: uuid.UUID):
    """校验节点存在且属于同一张导图"""
    result = await db.execute(
        select(MindMapNode.id).where(
            MindMapNode.mind_map_id == map_id,
            MindMapNode.id.in_(node_ids),
        )
    )
    found = {row[0] for row in result.all()}
    for nid in node_ids:
        if nid not in found:
            raise HTTPException(status_code=404, detail=f"节点 {nid} 不存在或不属于该导图")


@router.post("/{map_id}/edges", response_model=MindMapEdgeSchema)
async def add_edge(
    map_id: str,
    request: CreateEdgeRequest,
    db: AsyncSession = Depends(get_db),
):
    """新建连线"""
    map_uuid = uuid.UUID(map_id)
    m = await db.get(MindMap, map_uuid)
    if not m:
        raise HTTPException(status_code=404, detail="思维导图不存在")

    source_uuid = uuid.UUID(request.source)
    target_uuid = uuid.UUID(request.target)

    if source_uuid == target_uuid:
        raise HTTPException(status_code=400, detail="不允许节点连接到自身")

    await _ensure_nodes_exist(db, map_uuid, source_uuid, target_uuid)

    # 防止重复边
    dup = await db.execute(
        select(MindMapEdge).where(
            MindMapEdge.mind_map_id == map_uuid,
            MindMapEdge.source_id == source_uuid,
            MindMapEdge.target_id == target_uuid,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该连线已存在")

    edge = MindMapEdge(
        mind_map_id=map_uuid,
        source_id=source_uuid,
        target_id=target_uuid,
        edge_type=request.edge_type,
        color=request.color,
        stroke_width=request.stroke_width,
        has_arrow=request.has_arrow,
        animated=request.animated,
        label=request.label,
        is_derived=False,
    )
    db.add(edge)
    await db.flush()

    return MindMapEdgeSchema(
        id=str(edge.id),
        source=str(edge.source_id),
        target=str(edge.target_id),
        edge_type=edge.edge_type,
        color=edge.color,
        stroke_width=edge.stroke_width,
        has_arrow=edge.has_arrow,
        animated=edge.animated,
        label=edge.label,
        is_derived=edge.is_derived,
    )


@router.patch("/{map_id}/edges/{edge_id}", response_model=MindMapEdgeSchema)
async def update_edge(
    map_id: str,
    edge_id: str,
    request: UpdateEdgeRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新连线（包括重连端点、改样式）。"""
    map_uuid = uuid.UUID(map_id)

    edge = await db.get(MindMapEdge, uuid.UUID(edge_id))
    if not edge or edge.mind_map_id != map_uuid:
        raise HTTPException(status_code=404, detail="连线不存在")

    # 重连端点
    if request.source is not None:
        new_source = uuid.UUID(request.source)
        await _ensure_nodes_exist(db, map_uuid, new_source)
        edge.source_id = new_source
    if request.target is not None:
        new_target = uuid.UUID(request.target)
        await _ensure_nodes_exist(db, map_uuid, new_target)
        edge.target_id = new_target
    if edge.source_id == edge.target_id:
        raise HTTPException(status_code=400, detail="不允许节点连接到自身")

    # 改样式
    if request.edge_type is not None:
        edge.edge_type = request.edge_type
    if request.color is not None:
        edge.color = request.color
    if request.stroke_width is not None:
        edge.stroke_width = request.stroke_width
    if request.has_arrow is not None:
        edge.has_arrow = request.has_arrow
    if request.animated is not None:
        edge.animated = request.animated
    if request.label is not None:
        edge.label = request.label

    await db.flush()

    return MindMapEdgeSchema(
        id=str(edge.id),
        source=str(edge.source_id),
        target=str(edge.target_id),
        edge_type=edge.edge_type,
        color=edge.color,
        stroke_width=edge.stroke_width,
        has_arrow=edge.has_arrow,
        animated=edge.animated,
        label=edge.label,
        is_derived=edge.is_derived,
    )


@router.delete("/{map_id}/edges/{edge_id}")
async def delete_edge(
    map_id: str,
    edge_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除连线。"""
    map_uuid = uuid.UUID(map_id)

    edge = await db.get(MindMapEdge, uuid.UUID(edge_id))
    if not edge or edge.mind_map_id != map_uuid:
        raise HTTPException(status_code=404, detail="连线不存在")

    await db.delete(edge)
    await db.flush()
    return {"message": "删除成功"}


@router.get("/{map_id}/nodes/{node_id}/questions", response_model=NodeQuestionsResponse)
async def get_node_questions(
    map_id: str,
    node_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    node = await db.get(MindMapNode, uuid.UUID(node_id))
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    if node.module_id:
        query = select(Question).where(Question.module_id == node.module_id)
    else:
        module_result = await db.execute(
            select(Module).where(Module.name == node.label)
        )
        module = module_result.scalar_one_or_none()
        if not module:
            return NodeQuestionsResponse(total=0, page=page, page_size=page_size, items=[])
        query = select(Question).where(Question.module_id == module.id)

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    items_result = await db.execute(
        query.order_by(Question.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    questions = items_result.scalars().all()

    items = []
    for q in questions:
        items.append(NodeQuestionItem(
            id=str(q.id),
            content=q.content,
            answer=q.answer,
            explanation=q.explanation,
            source=q.source,
            difficulty=q.difficulty,
            mastery=q.mastery,
            created_at=q.created_at,
        ))

    return NodeQuestionsResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


# ===== 题目导入到思维导图 =====

@router.post("/{map_id}/import-questions", response_model=ImportQuestionsResponse)
async def import_questions_to_mindmap(
    map_id: str,
    request: ImportQuestionsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    批量导入题目到思维导图。
    流程：去重 → 分类确认 → 创建Question → 更新导图节点
    """
    mindmap = await db.get(MindMap, uuid.UUID(map_id))
    if not mindmap:
        raise HTTPException(status_code=404, detail="思维导图不存在")

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

            # 去重检查
            if not request.allow_duplicate:
                is_dup, existing = await check_duplicate_question(
                    db, sanitized, mindmap.id
                )
                if is_dup:
                    failed.append({
                        "index": i,
                        "content_preview": item.content[:50],
                        "reason": "题目已存在于该思维导图中",
                        "existing_question_id": str(existing.id) if existing else None,
                    })
                    continue

            # 确定分类
            primary_module = mindmap.root_module
            secondary_module = item.secondary_module

            if item.module_id:
                module = await db.get(Module, uuid.UUID(item.module_id))
                if module:
                    secondary_module = module.name
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

            # 查找模块ID
            module_id = None
            if secondary_module:
                module_query = select(Module).where(Module.name == secondary_module)
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
                source="手动导入",
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

    # 批量更新思维导图
    mindmap_update = None
    if questions_data_for_mindmap:
        try:
            mindmap_update = await batch_update_mindmap(
                db, mindmap.id, questions_data_for_mindmap
            )
        except Exception as e:
            logger.error(f"批量更新思维导图失败: {e}")

    await db.commit()

    return ImportQuestionsResponse(
        imported_count=len(imported_ids),
        imported_ids=imported_ids,
        failed=failed,
        mindmap_update=mindmap_update,
    )
