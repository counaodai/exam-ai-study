import uuid
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime


def _uuid_to_str(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    return v


class SendMessageRequest(BaseModel):
    content: str
    conversation_id: Optional[str] = None


class ClassificationResult(BaseModel):
    module: str
    sub_module: str
    confidence: float
    reason: str


class MindMapUpdateResult(BaseModel):
    updated: bool = False
    mindmap_id: Optional[str] = None
    node_label: Optional[str] = None
    question_count: int = 0
    mastery: int = 0
    should_generate_method: bool = False
    method_id: Optional[str] = None


class SourceItem(BaseModel):
    content: str
    source: str
    page: Optional[int] = None
    score: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def handle_similarity_field(cls, data: dict) -> dict:
        if isinstance(data, dict):
            if "score" not in data and "similarity" in data:
                data["score"] = data.pop("similarity")
            if data.get("score") is None:
                data["score"] = 0.0
        return data


class ChatMessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    question_id: Optional[str] = None
    module_id: Optional[str] = None
    classification: Optional[ClassificationResult] = None
    sources: Optional[list[SourceItem]] = None
    mindmap_update: Optional[MindMapUpdateResult] = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", "conversation_id", "question_id", "module_id", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        return _uuid_to_str(v)


class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        return _uuid_to_str(v)


class UpdateClassificationRequest(BaseModel):
    module: str
    sub_module: Optional[str] = None


class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[ChatMessageResponse]
