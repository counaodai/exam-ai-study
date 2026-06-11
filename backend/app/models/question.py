import uuid
from sqlalchemy import String, Integer, SmallInteger, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Question(BaseModel):
    __tablename__ = "questions"

    content: Mapped[str] = mapped_column(Text)
    options: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    module_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("modules.id"), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_doc_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mastery: Mapped[int] = mapped_column(SmallInteger, default=0)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否为有效提问，无效提问不计入统计")
