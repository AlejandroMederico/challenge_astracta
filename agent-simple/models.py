from typing import List, Optional
import uuid
from pydantic import BaseModel, Field


class SessionBase(BaseModel):
    locales: List[str]


class Session(SessionBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class QuestionRequest(BaseModel):
    question: Optional[str] = ""


class AgentStep(BaseModel):
    action: str = "message"
    value: str


class QuestionResponse(BaseModel):
    steps: List[AgentStep]
