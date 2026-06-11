import uuid
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


def _uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v


class NodePosition(BaseModel):
    x: float = 0.0
    y: float = 0.0


class NodeMetadata(BaseModel):
    is_auto_generated: bool = False
    source_questions: list[str] = []
    method_summary: Optional[str] = None


class MindMapNodeResponse(BaseModel):
    id: str
    label: str
    type: str
    parent_id: Optional[str] = None
    level: int = 0
    question_count: int = 0
    mastery: int = 0
    content: Optional[str] = None
    metadata: NodeMetadata = NodeMetadata()
    position: NodePosition = NodePosition()

    model_config = {"from_attributes": True}

    @field_validator("id", "parent_id", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        return _uuid_to_str(v)


class MindMapEdge(BaseModel):
    """思维导图连线响应模型"""
    id: str
    source: str
    target: str
    edge_type: str = "default"
    color: str = "#409EFF"
    stroke_width: int = 2
    has_arrow: bool = True
    animated: bool = False
    label: Optional[str] = None
    is_derived: bool = False

    @field_validator("id", "source", "target", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        return _uuid_to_str(v)


class MindMapResponse(BaseModel):
    id: str
    title: str
    root_module: str
    nodes: list[MindMapNodeResponse] = []
    edges: list[MindMapEdge] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        return _uuid_to_str(v)


class CreateMindMapRequest(BaseModel):
    title: str
    root_module: str


class UpdateNodeRequest(BaseModel):
    label: Optional[str] = None
    content: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    parent_id: Optional[str] = None


class CreateNodeRequest(BaseModel):
    label: str
    type: str = "topic"
    parent_id: Optional[str] = None
    content: Optional[str] = None


class CreateNodeResponseData(BaseModel):
    node: MindMapNodeResponse
    edge: Optional[MindMapEdge] = None


class DeleteNodeResponse(BaseModel):
    message: str
    deleted_count: int


# ===== 边（连线）请求模型 =====

class CreateEdgeRequest(BaseModel):
    """新建连线请求"""
    source: str
    target: str
    edge_type: str = "default"
    color: str = "#409EFF"
    stroke_width: int = 2
    has_arrow: bool = True
    animated: bool = False
    label: Optional[str] = None


class UpdateEdgeRequest(BaseModel):
    """更新连线（含重连端点、改样式）"""
    source: Optional[str] = None
    target: Optional[str] = None
    edge_type: Optional[str] = None
    color: Optional[str] = None
    stroke_width: Optional[int] = None
    has_arrow: Optional[bool] = None
    animated: Optional[bool] = None
    label: Optional[str] = None


class NodeQuestionItem(BaseModel):
    id: str
    content: str
    answer: Optional[str] = None
    explanation: Optional[str] = None
    source: Optional[str] = None
    difficulty: Optional[int] = None
    mastery: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        return _uuid_to_str(v)


class NodeQuestionsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[NodeQuestionItem]
