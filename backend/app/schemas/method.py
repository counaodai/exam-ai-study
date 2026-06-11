import uuid
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


def _uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v


class MethodRecognition(BaseModel):
    title: str = ""
    content: str = ""


class MethodStep(BaseModel):
    step: int
    title: str
    description: str
    example: str = ""


class MethodTrap(BaseModel):
    trap: str
    solution: str


class MethodSummaryResponse(BaseModel):
    id: str
    module_id: Optional[str] = None
    method_name: str
    recognition: Optional[MethodRecognition] = None
    steps: list[MethodStep] = []
    traps: list[MethodTrap] = []
    quick_tips: list[str] = []
    key_formulas: list[str] = []
    summary: Optional[str] = None
    question_count: Optional[int] = None
    source_question_ids: list[str] = []
    is_auto_generated: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", "module_id", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        return _uuid_to_str(v)


class GenerateMethodRequest(BaseModel):
    module_id: str


class UpdateMethodRequest(BaseModel):
    method_name: Optional[str] = None
    recognition: Optional[MethodRecognition] = None
    steps: Optional[list[MethodStep]] = None
    traps: Optional[list[MethodTrap]] = None
    quick_tips: Optional[list[str]] = None
    key_formulas: Optional[list[str]] = None
    summary: Optional[str] = None
