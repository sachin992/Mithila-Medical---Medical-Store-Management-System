from datetime import datetime
from pydantic import BaseModel


class AssistantThreadCreate(BaseModel):
    title: str
    mode: str = "readonly"
    retention_days: int = 30


class AssistantMessageIn(BaseModel):
    thread_id: int
    message: str
    mode: str = "readonly"
    confirm_write: bool = False


class AssistantMessageOut(BaseModel):
    thread_id: int
    mode: str
    action_type: str
    sql: str | None
    rows: list[dict]
    summary: str
    created_at: datetime


class ReportTemplateOut(BaseModel):
    key: str
    title: str
    prompt: str
