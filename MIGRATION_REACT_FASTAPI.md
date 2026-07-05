# React + FastAPI Migration Summary

This repository now contains a new stack alongside the existing Streamlit code.

## New folders
- `backend_fastapi`: FastAPI API server with SQLAlchemy and Alembic
- `frontend_react`: React SPA powered by Vite

## Dockerized setup
- Root `docker-compose.yml` orchestrates both services.
- `backend_fastapi/Dockerfile` builds and runs FastAPI on port `8000`.
- `frontend_react/Dockerfile` builds React and serves via Nginx on port `5173`.

Run everything:

```bash
docker compose up --build -d
```

Check services:

```bash
docker compose ps
```

URLs:
- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`

Stop everything:

```bash
docker compose down
```

## Covered enhancement items
1. Cart + multi-item orders: done via `/api/orders/cart` and `/api/orders/checkout`
2. Payment logic + invoice + cancellation window: done in orders/payment service
3. Search filters: medicine API supports name/category/manufacturer/price/expiry filters
4. Tracking with medicine names + timeline: done in order response model
5. Staff tools: edit medicine, CSV import, low-stock reorder suggestions
6. Notifications: SMS/email logging hook on state changes
7. Assistant split read/write: done with explicit `mode` and `confirm_write`
8. Structured assistant output: returns action, SQL, rows, summary
9. SQL guardrails: blocks dangerous SQL and out-of-scope tables
10. Per-staff thread + retention: thread endpoints and cleanup implemented
11. Analytics templates: `/api/assistant/templates`
12. Layered architecture: `api`, `services`, `models`, `schemas`, `db`, `core`
13. Shared DB lifecycle: central `SessionLocal` and dependency
14. Migration baseline: Alembic initial migration script
15. Integrity constraints + indexes: model constraints and index definitions included

## Next production hardening tasks
- Add real gateway integration for UPI/card callbacks
- Add actual SMS/email providers
- Add E2E tests and CI pipeline
- Add stricter role/permission matrix and audit logs
