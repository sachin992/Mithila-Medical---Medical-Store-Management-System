from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import AdminChatMemory


class PostgresSaver:
    """Short-term memory store for admin analytics chat backed by PostgreSQL table."""

    def __init__(self, db: Session, ttl_minutes: int = 180):
        self.db = db
        self.ttl_minutes = ttl_minutes

    def save_message(self, thread_id: int, admin_user_id: int, role: str, content: str) -> None:
        now = datetime.utcnow()
        memory = AdminChatMemory(
            thread_id=thread_id,
            admin_user_id=admin_user_id,
            role=role,
            content=content,
            created_at=now,
            expires_at=now + timedelta(minutes=self.ttl_minutes),
        )
        self.db.add(memory)

    def get_recent_messages(self, thread_id: int, admin_user_id: int, limit: int = 30) -> list[dict]:
        rows = (
            self.db.query(AdminChatMemory)
            .filter(
                AdminChatMemory.thread_id == thread_id,
                AdminChatMemory.admin_user_id == admin_user_id,
                AdminChatMemory.expires_at > datetime.utcnow(),
            )
            .order_by(AdminChatMemory.created_at.asc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": row.id,
                "role": row.role,
                "content": row.content,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def cleanup_expired(self, admin_user_id: int | None = None) -> int:
        query = self.db.query(AdminChatMemory).filter(AdminChatMemory.expires_at <= datetime.utcnow())
        if admin_user_id is not None:
            query = query.filter(AdminChatMemory.admin_user_id == admin_user_id)

        expired = query.all()
        for item in expired:
            self.db.delete(item)
        return len(expired)
