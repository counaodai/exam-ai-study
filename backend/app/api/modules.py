import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.module import Module
from app.schemas.module import (
    ModuleResponse,
    ModuleTreeNode,
    CreateModuleRequest,
    UpdateModuleRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/modules", tags=["模块分类"])


def build_tree(modules: list[Module], parent_id: uuid.UUID | None = None) -> list[dict]:
    tree = []
    for m in modules:
        if m.parent_id == parent_id:
            node = {
                "id": m.id,
                "name": m.name,
                "parent_id": m.parent_id,
                "level": m.level,
                "description": m.description,
                "sort_order": m.sort_order,
                "is_preset": m.is_preset,
                "children": build_tree(modules, m.id),
            }
            tree.append(node)
    tree.sort(key=lambda x: x["sort_order"])
    return tree


@router.get("/tree", response_model=list[ModuleTreeNode])
async def get_module_tree(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Module).order_by(Module.sort_order, Module.name)
    )
    modules = result.scalars().all()
    return build_tree(modules)


@router.get("", response_model=list[ModuleResponse])
async def get_modules(
    level: int | None = None,
    parent_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Module).order_by(Module.sort_order, Module.name)
    if level is not None:
        query = query.where(Module.level == level)
    if parent_id is not None:
        query = query.where(Module.parent_id == uuid.UUID(parent_id))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(module_id: str, db: AsyncSession = Depends(get_db)):
    module = await db.get(Module, uuid.UUID(module_id))
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    return module


@router.post("", response_model=ModuleResponse)
async def create_module(
    request: CreateModuleRequest,
    db: AsyncSession = Depends(get_db),
):
    if request.parent_id:
        parent = await db.get(Module, uuid.UUID(request.parent_id))
        if not parent:
            raise HTTPException(status_code=404, detail="父模块不存在")
        if request.level <= parent.level:
            raise HTTPException(status_code=400, detail="子模块层级必须大于父模块")

    module = Module(
        name=request.name,
        parent_id=uuid.UUID(request.parent_id) if request.parent_id else None,
        level=request.level,
        description=request.description,
        sort_order=request.sort_order,
        is_preset=False,
    )
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str,
    request: UpdateModuleRequest,
    db: AsyncSession = Depends(get_db),
):
    module = await db.get(Module, uuid.UUID(module_id))
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")

    if request.name is not None:
        module.name = request.name
    if request.description is not None:
        module.description = request.description
    if request.sort_order is not None:
        module.sort_order = request.sort_order

    await db.commit()
    await db.refresh(module)
    return module


@router.delete("/{module_id}")
async def delete_module(module_id: str, db: AsyncSession = Depends(get_db)):
    module = await db.get(Module, uuid.UUID(module_id))
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")

    if module.is_preset:
        raise HTTPException(status_code=400, detail="预置模块不可删除")

    children_result = await db.execute(
        select(Module).where(Module.parent_id == module.id)
    )
    if children_result.scalars().first():
        raise HTTPException(status_code=400, detail="该模块下存在子模块，请先删除子模块")

    await db.delete(module)
    return {"message": "删除成功"}
