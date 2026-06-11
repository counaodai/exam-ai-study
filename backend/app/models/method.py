import uuid
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class MethodSummary(BaseModel):
    __tablename__ = "method_summaries"

    module_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("modules.id"), nullable=True)
    method_name: Mapped[str] = mapped_column(String(200))
    recognition: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    steps: Mapped[list] = mapped_column(JSON)
    traps: Mapped[list | None] = mapped_column(JSON, nullable=True)
    quick_tips: Mapped[list | None] = mapped_column(JSON, nullable=True)
    key_formulas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_question_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=True)
