import uuid
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Module(BaseModel):
    __tablename__ = "modules"

    name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("modules.id"), nullable=True)
    level: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)

    children: Mapped[list["Module"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    parent: Mapped["Module | None"] = relationship(back_populates="children", remote_side="Module.id")
