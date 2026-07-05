# Mithila Medical React Frontend

React SPA for customers and staff, connected to the FastAPI backend.

## Features
- Login/signup screens
- Medicine browsing with filters
- Cart and checkout flow
- Orders timeline view
- Admin inventory operations UI
- Admin analytics chatbot UI with saved prompts and chat history

## Environment
Optional `.env`:
```env
VITE_API_BASE=http://localhost:8000/api
```

## Local Run
```bash
npm install
npm run dev
```

## Docker
From repository root:
```bash
docker compose up --build -d frontend
```

Frontend URL: http://localhost:5173
