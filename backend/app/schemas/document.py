from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ChunkType(str, Enum):
    QUESTION = "question"
    KNOWLEDGE = "knowledge"
    METHOD = "method"


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    file_path: str
    module: Optional[str] = None
    status: DocumentStatus
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class ChunkMetadata(BaseModel):
    page: Optional[int] = None
    chapter: Optional[str] = None
    question_number: Optional[int] = None
    year: Optional[str] = None
    tags: list[str] = []


class DocumentChunk(BaseModel):
    id: str
    content: str
    source: str
    module: Optional[str] = None
    chunk_type: ChunkType
    metadata: ChunkMetadata
