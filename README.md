# EduWatch Starter (Next.js + FastAPI)

Functional starter for a one-day MVP:
- `frontend`: Next.js UI (dashboard + item detail + watchlist + AI tip trigger)
- `backend`: FastAPI service with SQLite, seeded mock data, and core endpoints

## 1) Run backend

```bash
cd backend
uv sync
uv run python seed.py
uv run uvicorn app.main:app --reload --port 8000
```

Backend API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

## 2) Run frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend URL: `http://localhost:3000`

## 3) Core endpoints

- `GET /health`
- `GET /items?search=&category=&max_price=`
- `GET /items/{id}`
- `GET /items/{id}/history`
- `POST /watchlist`
- `GET /watchlist/{user_tag}`
- `POST /insights/{item_id}`

## 4) Demo flow

1. Open dashboard and filter by category/budget.
2. Open an item to see price history chart.
3. Set target price in watchlist.
4. Generate insight for buy-now vs wait recommendation.
