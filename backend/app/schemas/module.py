import uuid
from datetime import datetime
from pydantic import BaseModel


class ModuleResponse(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None = None
    level: int
    description: str | None = None
    sort_order: int = 0
    is_preset: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ModuleTreeNode(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None = None
    level: int
    description: str | None = None
    sort_order: int = 0
    is_preset: bool = False
    children: list["ModuleTreeNode"] = []

    model_config = {"from_attributes": True}


class CreateModuleRequest(BaseModel):
    name: str
    parent_id: str | None = None
    level: int = 1
    description: str | None = None
    sort_order: int = 0


class UpdateModuleRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    sort_order: int | None = None
