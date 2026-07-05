from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from sqlalchemy import text
from sqlalchemy.orm import Session

SAFE_TABLES = {"medicines", "orders", "order_items", "order_events", "payments"}
BLOCKED_SQL_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "truncate",
    "alter",
    "create",
    "grant",
    "revoke",
    "copy",
    "merge",
}
DOMAIN_KEYWORDS = {
    "inventory",
    "stock",
    "medicine",
    "medicines",
    "cost",
    "value",
    "available",
    "total",
    "sales",
    "revenue",
    "order",
    "orders",
    "top selling",
    "low stock",
    "restock",
}

SCHEMA_HINT = """
Allowed tables and useful columns:
- medicines(id, medicine_name, quantity, price, category, manufacturer, expiry_date, created_at)
- orders(id, user_id, customer_name, status, total_price, created_at)
- order_items(id, order_id, medicine_id, medicine_name_snapshot, unit_price, quantity, line_total)
- order_events(id, order_id, event_type, note, created_at)
- payments(id, order_id, method, status, amount, created_at)
""".strip()


class AssistantState(TypedDict, total=False):
    question: str
    memory: list[dict[str, Any]]
    action_type: str
    sql: str | None
    rows: list[dict[str, Any]]
    summary: str
    error: str | None


def _looks_in_domain(question: str) -> bool:
    q = question.lower()
    return any(keyword in q for keyword in DOMAIN_KEYWORDS)


def _extract_sql(raw: str) -> str:
    block_match = re.search(r"```sql\s*(.*?)\s*```", raw, flags=re.IGNORECASE | re.DOTALL)
    if block_match:
        return block_match.group(1).strip()

    stripped = raw.strip()
    if stripped.lower().startswith("select"):
        return stripped

    line_match = re.search(r"(select\s+.+)", stripped, flags=re.IGNORECASE | re.DOTALL)
    if line_match:
        return line_match.group(1).strip()

    return stripped


def _normalize_sql(sql: str) -> str:
    cleaned = sql.strip().rstrip(";")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _extract_table_names(sql: str) -> set[str]:
    matches = re.findall(r"\b(?:from|join)\s+([a-zA-Z_][\w\.]*)", sql, flags=re.IGNORECASE)
    tables = set()
    for value in matches:
        name = value.split(".")[-1].lower()
        tables.add(name)
    return tables


def _validate_sql_guardrails(sql: str) -> tuple[bool, str, str | None]:
    if not sql:
        return False, "No SQL was generated.", None

    candidate = _normalize_sql(sql)
    lower = candidate.lower()

    if not lower.startswith("select"):
        return False, "Only read-only SELECT queries are allowed.", None

    if "--" in lower or "/*" in lower or "*/" in lower:
        return False, "SQL comments are not allowed.", None

    if ";" in candidate:
        return False, "Multiple statements are not allowed.", None

    if any(re.search(rf"\b{kw}\b", lower) for kw in BLOCKED_SQL_KEYWORDS):
        return False, "Blocked SQL keyword detected.", None

    tables = _extract_table_names(candidate)
    if not tables:
        return False, "SQL must reference at least one allowed table.", None

    out_of_scope = sorted(t for t in tables if t not in SAFE_TABLES)
    if out_of_scope:
        return False, f"Out-of-scope table(s): {', '.join(out_of_scope)}", None

    return True, "ok", candidate


def _enforce_limit(sql: str, max_rows: int) -> str:
    if re.search(r"\blimit\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql} LIMIT {max_rows}"


def _fallback_sql_for_question(question: str) -> str | None:
    q = question.strip().lower()

    if "total cost" in q and ("inventory" in q or "medicine" in q or "medicines" in q or "stock" in q):
        return "SELECT COALESCE(SUM(price * quantity), 0) AS total_inventory_cost FROM medicines"

    if ("how many" in q or "total" in q) and ("medicine" in q or "medicines" in q) and ("available" in q or "inventory" in q):
        return "SELECT COALESCE(SUM(quantity), 0) AS total_units_available FROM medicines"

    if "low stock" in q or "restock" in q:
        return "SELECT medicine_name, quantity, price FROM medicines WHERE quantity < 10 ORDER BY quantity ASC"

    if "top selling" in q or "best selling" in q:
        return (
            "SELECT medicine_name_snapshot AS medicine_name, SUM(quantity) AS units_sold, "
            "SUM(line_total) AS revenue FROM order_items GROUP BY medicine_name_snapshot "
            "ORDER BY units_sold DESC LIMIT 10"
        )

    if "revenue" in q and "last month" in q:
        return (
            "SELECT COALESCE(SUM(total_price), 0) AS total_revenue_last_month "
            "FROM orders WHERE status='DELIVERED' "
            "AND created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month' "
            "AND created_at < DATE_TRUNC('month', CURRENT_DATE)"
        )

    if "revenue" in q:
        return "SELECT COALESCE(SUM(total_price), 0) AS total_revenue FROM orders WHERE status='DELIVERED'"

    return None


class LlmSqlAssistant:
    def __init__(
        self,
        db: Session,
        *,
        model: str,
        api_key: str | None,
        timeout_seconds: int,
        max_rows: int = 200,
    ):
        self.db = db
        self.max_rows = max_rows
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0,
            timeout=timeout_seconds,
        )
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AssistantState)
        graph.add_node("classify", self._classify_node)
        graph.add_node("to_sql", self._to_sql_node)
        graph.add_node("guardrails", self._guardrails_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("summarize", self._summarize_node)

        graph.set_entry_point("classify")
        graph.add_edge("classify", "to_sql")
        graph.add_edge("to_sql", "guardrails")
        graph.add_edge("guardrails", "execute")
        graph.add_edge("execute", "summarize")
        graph.add_edge("summarize", END)

        return graph.compile()

    def _classify_node(self, state: AssistantState) -> AssistantState:
        question = state["question"]
        if not _looks_in_domain(question):
            return {
                "action_type": "blocked",
                "summary": "I can only answer questions about inventory, sales, or revenue analytics.",
                "rows": [],
                "sql": None,
            }
        return {"action_type": "in_scope"}

    def _to_sql_node(self, state: AssistantState) -> AssistantState:
        if state.get("action_type") == "blocked":
            return {"error": state.get("error")}

        fallback_sql = _fallback_sql_for_question(state["question"])

        memory = state.get("memory", [])[-8:]
        memory_text = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in memory])

        prompt = (
            "You are an analytics SQL generator for a medical store system.\n"
            "Generate exactly one PostgreSQL SELECT query for the user question.\n"
            "Scope is strictly inventory, sales, and revenue analytics.\n"
            "Use only allowed tables. Never generate write/DDL statements.\n"
            f"{SCHEMA_HINT}\n"
            "If question is out of scope, reply exactly: OUT_OF_SCOPE\n"
            "Return SQL only, no explanation.\n"
            f"Conversation memory:\n{memory_text or '(none)'}\n"
            f"User question: {state['question']}"
        )

        try:
            raw = self.llm.invoke(prompt).content
        except Exception:
            if fallback_sql:
                return {"sql": fallback_sql}
            return {
                "action_type": "blocked",
                "summary": "LLM is unavailable right now. Please verify OpenAI configuration and try again.",
                "rows": [],
                "sql": None,
            }
        raw_text = raw if isinstance(raw, str) else str(raw)

        if raw_text.strip().upper() == "OUT_OF_SCOPE":
            if fallback_sql:
                return {"sql": fallback_sql}
            return {
                "action_type": "blocked",
                "summary": "I can only answer questions about inventory, sales, or revenue analytics.",
                "rows": [],
                "sql": None,
            }

        return {"sql": _extract_sql(raw_text)}

    def _guardrails_node(self, state: AssistantState) -> AssistantState:
        if state.get("action_type") == "blocked":
            return {"error": state.get("error")}

        is_valid, reason, normalized_sql = _validate_sql_guardrails(state.get("sql") or "")
        if not is_valid:
            return {
                "action_type": "blocked",
                "summary": f"Blocked by SQL guardrails: {reason}",
                "rows": [],
                "sql": None,
            }

        return {"sql": _enforce_limit(normalized_sql or "", self.max_rows), "action_type": "read"}

    def _execute_node(self, state: AssistantState) -> AssistantState:
        if state.get("action_type") != "read":
            return {"error": state.get("error")}

        try:
            result = self.db.execute(text(state["sql"]))
            rows = [dict(row._mapping) for row in result.fetchall()]
            self.db.rollback()
            return {"rows": rows}
        except Exception as exc:
            self.db.rollback()
            return {
                "action_type": "blocked",
                "summary": "Blocked by SQL guardrails: SQL execution failed safely.",
                "rows": [],
                "sql": None,
                "error": str(exc),
            }

    def _summarize_node(self, state: AssistantState) -> AssistantState:
        if state.get("action_type") != "read":
            return {"error": state.get("error")}

        rows = state.get("rows", [])
        if not rows:
            return {"summary": "No matching records found."}

        sample = rows[:20]
        prompt = (
            "You are an analytics assistant.\n"
            "Answer using only inventory/sales/revenue context.\n"
            "If the question asks outside this scope, refuse.\n"
            "Provide a concise answer based on SQL rows.\n"
            f"Question: {state['question']}\n"
            f"Rows (JSON): {json.dumps(sample, default=str)}\n"
        )
        try:
            response = self.llm.invoke(prompt).content
            summary = response if isinstance(response, str) else str(response)
            return {"summary": summary.strip() or f"Returned {len(rows)} rows"}
        except Exception:
            return {"summary": f"Returned {len(rows)} rows"}

    def run(self, question: str, memory: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        if not question.strip():
            return {
                "action_type": "blocked",
                "sql": None,
                "rows": [],
                "summary": "Question cannot be empty.",
                "created_at": datetime.utcnow(),
            }

        state: AssistantState = {"question": question.strip(), "memory": memory or []}
        result = self.graph.invoke(state)

        return {
            "action_type": result.get("action_type", "blocked"),
            "sql": result.get("sql"),
            "rows": result.get("rows", []),
            "summary": result.get("summary", "No response generated."),
            "created_at": datetime.utcnow(),
        }
