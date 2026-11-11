from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    created_at: datetime
    title: str | None = None
    messages: list[MessageResponse] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    id: str
    created_at: datetime
    title: str | None = None
