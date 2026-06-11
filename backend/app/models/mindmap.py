import uuid
from sqlalchemy import String, Integer, SmallInteger, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class MindMap(BaseModel):
    __tablename__ = "mind_maps"

    title: Mapped[str] = mapped_column(String(200))
    root_module: Mapped[str] = mapped_column(String(100))

    nodes: Mapped[list["MindMapNode"]] = relationship(back_populates="mind_map", cascade="all, delete-orphan")
    edges: Mapped[list["MindMapEdge"]] = relationship(back_populates="mind_map", cascade="all, delete-orphan")


class MindMapNode(BaseModel):
    __tablename__ = "mind_map_nodes"

    mind_map_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mind_maps.id", ondelete="CASCADE"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("mind_map_nodes.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(20))
    module_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("modules.id"), nullable=True)
    question_count: Mapped[int] = mapped_column(Integer, default=0)
    mastery: Mapped[int] = mapped_column(SmallInteger, default=0)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    method_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    position_x: Mapped[float] = mapped_column(Float, default=0)
    position_y: Mapped[float] = mapped_column(Float, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    mind_map: Mapped["MindMap"] = relationship(back_populates="nodes")


class MindMapEdge(BaseModel):
    """思维导图连线（独立图结构，支持任意连接）"""
    __tablename__ = "mind_map_edges"

    mind_map_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mind_maps.id", ondelete="CASCADE"))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mind_map_nodes.id", ondelete="CASCADE"))
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mind_map_nodes.id", ondelete="CASCADE"))
    # 连线类型：default(贝塞尔) / straight / step / smoothstep
    edge_type: Mapped[str] = mapped_column(String(20), default="default")
    # 连线颜色（hex）
    color: Mapped[str] = mapped_column(String(20), default="#409EFF")
    # 连线粗细
    stroke_width: Mapped[int] = mapped_column(SmallInteger, default=2)
    # 是否带箭头
    has_arrow: Mapped[bool] = mapped_column(Boolean, default=True)
    # 是否动画
    animated: Mapped[bool] = mapped_column(Boolean, default=False)
    # 连线标签文本
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 是否由 parent_id 自动派生（区分手动添加的边）
    is_derived: Mapped[bool] = mapped_column(Boolean, default=False)

    mind_map: Mapped["MindMap"] = relationship(back_populates="edges")
