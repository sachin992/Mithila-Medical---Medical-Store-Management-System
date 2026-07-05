# Mithila Medical FastAPI Backend

Backend service for authentication, medicines, orders, admin operations, and analytics chat workflows.

## Features
- JWT auth (customer/admin)
- Medicines API with filters
- Cart + multi-item checkout
- Payment records (COD/UPI/CARD)
- Order timeline and invoice payload
- Cancellation window enforcement
- Staff medicine edit + CSV bulk import
- Reorder suggestion endpoint
- Notification logging hooks
- Admin analytics chatbot endpoints (LLM-based)
- LangChain + LangGraph orchestration with OpenAI `gpt-4o-mini`
- SQL guardrails (read-only SELECT, allowlisted tables, row limits, out-of-scope blocking)
- PostgresSaver short-term memory for admin chat

## Setup
1. Copy environment file:
```bash
cp .env.example .env
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run service:
```bash
uvicorn app.main:app --reload --port 8000
```

4. Configure LLM environment in `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT_SECONDS=30
```

## Docker
From repository root:
```bash
docker compose up --build -d backend
```

## Migrations
```bash
alembic upgrade head
```

## Important Endpoints
- Health: `GET /health`
- Auth: `/api/auth/*`
- Medicines: `/api/medicines`
- Orders: `/api/orders/*`
- Staff: `/api/staff/*`
- Assistant: `/api/assistant/*`

## Database
Configured by `DATABASE_URL` in `.env`.
Default: PostgreSQL via Docker (`postgresql+psycopg://postgres:postgres@postgres:5432/mithila_medical`).

## Admin bootstrap
Admin credentials are generated from backend env vars on startup:
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `ADMIN_FULL_NAME`

## LLM Chatbot Guardrails
- The assistant answers only inventory, sales, and revenue analytics questions.
- Questions outside this domain are blocked.
- Generated SQL must be a single read-only `SELECT` query.
- Allowed tables: `medicines`, `orders`, `order_items`, `order_events`, `payments`.
- Blocked SQL keywords include all write/DDL operations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.).
- Query results are capped with a server-side row limit.
