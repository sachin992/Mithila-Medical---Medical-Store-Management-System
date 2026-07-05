from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import get_settings
from app.db.session import get_db
from app.models import AssistantThread, User
from app.schemas.assistant import AssistantMessageIn, AssistantThreadCreate
from app.services.llm_sql_assistant import LlmSqlAssistant
from app.services.postgres_saver import PostgresSaver
from app.services.assistant_service import REPORT_TEMPLATES, cleanup_expired_threads, create_thread

router = APIRouter()
settings = get_settings()


@router.post("/threads")
def create_assistant_thread(
    payload: AssistantThreadCreate,
    db: Session = Depends(get_db),
    staff: User = Depends(require_admin),
):
    thread = create_thread(db, staff.id, payload.title, payload.mode, payload.retention_days)
    return {
        "id": thread.id,
        "title": thread.title,
        "mode": thread.mode,
        "retention_days": thread.retention_days,
        "created_at": thread.created_at,
    }


@router.get("/threads")
def list_threads(db: Session = Depends(get_db), staff: User = Depends(require_admin)):
    cleanup_expired_threads(db, staff.id)
    threads = (
        db.query(AssistantThread)
        .filter(AssistantThread.staff_user_id == staff.id)
        .order_by(AssistantThread.created_at.desc())
        .all()
    )
    return [
        {
            "id": thread.id,
            "title": thread.title,
            "mode": thread.mode,
            "retention_days": thread.retention_days,
            "created_at": thread.created_at,
        }
        for thread in threads
    ]


@router.get("/templates")
def list_report_templates(_: User = Depends(require_admin)):
    return REPORT_TEMPLATES


@router.post("/query")
def assistant_query(payload: AssistantMessageIn, db: Session = Depends(get_db), staff: User = Depends(require_admin)):
    thread = db.get(AssistantThread, payload.thread_id)
    if not thread or thread.staff_user_id != staff.id:
        raise HTTPException(status_code=404, detail="Thread not found")

    saver = PostgresSaver(db=db, ttl_minutes=settings.chat_memory_ttl_minutes)
    saver.cleanup_expired(admin_user_id=staff.id)
    saver.save_message(thread_id=thread.id, admin_user_id=staff.id, role="admin", content=payload.message)

    if not settings.openai_api_key:
        return {
            "thread_id": payload.thread_id,
            "mode": "readonly",
            "action_type": "blocked",
            "sql": None,
            "rows": [],
            "summary": "LLM is not configured. Set OPENAI_API_KEY on the backend service.",
            "created_at": thread.created_at,
        }

    memory = saver.get_recent_messages(thread_id=thread.id, admin_user_id=staff.id, limit=20)
    assistant = LlmSqlAssistant(
        db=db,
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        timeout_seconds=settings.openai_timeout_seconds,
    )

    result = assistant.run(question=payload.message, memory=memory)
    result["thread_id"] = payload.thread_id
    result["mode"] = "readonly"

    saver.save_message(thread_id=thread.id, admin_user_id=staff.id, role="assistant", content=result["summary"])
    db.commit()
    return result


@router.get("/threads/{thread_id}/memory")
def get_thread_memory(thread_id: int, db: Session = Depends(get_db), staff: User = Depends(require_admin)):
    thread = db.get(AssistantThread, thread_id)
    if not thread or thread.staff_user_id != staff.id:
        raise HTTPException(status_code=404, detail="Thread not found")

    saver = PostgresSaver(db=db, ttl_minutes=settings.chat_memory_ttl_minutes)
    saver.cleanup_expired(admin_user_id=staff.id)
    db.commit()
    return saver.get_recent_messages(thread_id=thread_id, admin_user_id=staff.id)
