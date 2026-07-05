from __future__ import annotations

import re
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import AssistantThread

WRITE_KEYWORDS = ("insert", "update")
BLOCKED_KEYWORDS = ("delete", "drop", "truncate", "alter")
SAFE_TABLES = {"medicines", "orders", "order_items", "order_events", "payments"}
MAX_ROWS = 200

REPORT_TEMPLATES = [
    {
        "key": "monthly_revenue",
        "title": "Monthly Revenue",
        "prompt": "SELECT TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month, SUM(total_price) AS revenue FROM orders WHERE status='DELIVERED' GROUP BY DATE_TRUNC('month', created_at) ORDER BY DATE_TRUNC('month', created_at) DESC",
    },
    {
        "key": "low_stock",
        "title": "Low Stock Medicines",
        "prompt": "SELECT medicine_name, quantity, price FROM medicines WHERE quantity < 20 ORDER BY quantity ASC",
    },
    {
        "key": "top_selling",
        "title": "Top Selling Medicines",
        "prompt": "SELECT medicine_name_snapshot AS medicine_name, SUM(quantity) AS units_sold FROM order_items GROUP BY medicine_name_snapshot ORDER BY units_sold DESC LIMIT 10",
    },
]


def _question_to_sql(question: str) -> str | None:
    q = question.strip().lower()

    if q.startswith(("select", "insert", "update")):
        return question

    if "revenue" in q and ("last year" in q or "previous year" in q):
        return (
            "SELECT TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month, SUM(total_price) AS revenue "
            "FROM orders WHERE status='DELIVERED' AND created_at >= NOW() - INTERVAL '1 year' "
            "GROUP BY DATE_TRUNC('month', created_at) ORDER BY DATE_TRUNC('month', created_at)"
        )

    if "revenue" in q and "last month" in q:
        return (
            "SELECT SUM(total_price) AS revenue_last_month FROM orders "
            "WHERE status='DELIVERED' "
            "AND DATE_TRUNC('month', created_at)=DATE_TRUNC('month', NOW() - INTERVAL '1 month')"
        )

    if "revenue" in q:
        return "SELECT SUM(total_price) AS total_revenue FROM orders WHERE status='DELIVERED'"

    if "top selling" in q or "best selling" in q:
        return (
            "SELECT medicine_name_snapshot AS medicine_name, SUM(quantity) AS units_sold, "
            "SUM(line_total) AS revenue FROM order_items GROUP BY medicine_name_snapshot "
            "ORDER BY units_sold DESC LIMIT 10"
        )

    if "low stock" in q or "restock" in q:
        return "SELECT medicine_name, quantity, price FROM medicines WHERE quantity < 10 ORDER BY quantity ASC"

    if "stock" in q and "of" in q:
        med_name = question.split("of", 1)[1].strip().strip("?.")
        if med_name:
            safe_name = med_name.replace("'", "''")
            return (
                "SELECT medicine_name, quantity, price FROM medicines "
                f"WHERE lower(medicine_name) LIKE lower('%{safe_name}%')"
            )

    if "pending order" in q:
        return "SELECT id, customer_name, total_price, created_at FROM orders WHERE status='PENDING' ORDER BY created_at DESC"

    return None


def _detect_action(sql: str) -> str:
    sql_clean = sql.strip().lower()
    if sql_clean.startswith("select"):
        return "read"
    if sql_clean.startswith("insert") or sql_clean.startswith("update"):
        return "write"
    return "blocked"


def _table_in_scope(sql: str) -> bool:
    lower_sql = sql.lower()
    return any(t in lower_sql for t in SAFE_TABLES)


def validate_sql(sql: str, mode: str, confirm_write: bool) -> tuple[bool, str, str]:
    lower_sql = sql.lower()
    if any(keyword in lower_sql for keyword in BLOCKED_KEYWORDS):
        return False, "blocked", "SQL includes blocked keywords"

    action = _detect_action(sql)
    if action == "blocked":
        return False, "blocked", "Only SELECT, INSERT, UPDATE are allowed"

    if not _table_in_scope(sql):
        return False, "blocked", "Query targets out-of-scope table"

    if action == "write":
        if mode != "write":
            return False, "blocked", "Write query requires write mode"
        if not confirm_write:
            return False, "blocked", "Write query requires explicit confirmation"

    return True, action, "ok"


def enforce_read_limit(sql: str) -> str:
    if re.search(r"\blimit\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql.rstrip(';')} LIMIT {MAX_ROWS}"


def run_structured_query(
    db: Session,
    thread_id: int,
    user_message: str,
    sql: str,
    mode: str,
    confirm_write: bool,
) -> dict:
    resolved_sql = _question_to_sql(user_message) if not sql else _question_to_sql(sql)
    if not resolved_sql:
        summary = "I could not map your question to a safe analytics query. Try asking about stock, low stock, revenue, or top selling medicines."
        return {
            "thread_id": thread_id,
            "mode": mode,
            "action_type": "blocked",
            "sql": None,
            "rows": [],
            "summary": summary,
            "created_at": datetime.utcnow(),
        }

    valid, action_type, reason = validate_sql(resolved_sql, mode, confirm_write)

    if not valid:
        summary = f"Blocked: {reason}"
        return {
            "thread_id": thread_id,
            "mode": mode,
            "action_type": "blocked",
            "sql": None,
            "rows": [],
            "summary": summary,
            "created_at": datetime.utcnow(),
        }

    exec_sql = enforce_read_limit(resolved_sql) if action_type == "read" else resolved_sql
    result = db.execute(text(exec_sql))

    rows: list[dict] = []
    if action_type == "read":
        rows = [dict(row._mapping) for row in result.fetchall()]
        summary = f"Returned {len(rows)} rows"
    else:
        db.commit()
        summary = f"Write query executed. Rows affected: {result.rowcount}"

    if action_type == "read":
        db.rollback()

    return {
        "thread_id": thread_id,
        "mode": mode,
        "action_type": action_type,
        "sql": exec_sql,
        "rows": rows,
        "summary": summary,
        "created_at": datetime.utcnow(),
    }


def create_thread(db: Session, staff_user_id: int, title: str, mode: str, retention_days: int) -> AssistantThread:
    thread = AssistantThread(
        staff_user_id=staff_user_id,
        title=title,
        mode=mode,
        retention_days=retention_days,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


def cleanup_expired_threads(db: Session, staff_user_id: int) -> int:
    threads = db.query(AssistantThread).filter(AssistantThread.staff_user_id == staff_user_id).all()
    deleted = 0
    now = datetime.utcnow()
    for thread in threads:
        expiry = thread.created_at + timedelta(days=thread.retention_days)
        if now > expiry:
            db.delete(thread)
            deleted += 1
    db.commit()
    return deleted
