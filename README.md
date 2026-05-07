# EduWatch Starter (Next.js + FastAPI)

Functional starter for a one-day MVP:
- `frontend`: Next.js UI (dashboard + item detail + watchlist + ML price prediction)
- `backend`: FastAPI service with SQLite, seeded mock data, and an XGBoost price-prediction model

## Prerequisites

- **Node.js 22 or 24 LTS** — do **not** use Node 25.
  Node 25 enables an experimental `localStorage` global on the server, which breaks Next.js SSR with errors like `localStorage.getItem is not a function`. If you have Node 25 installed, switch to 24:
  ```bash
  # install nvm if needed
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  # then in a new shell
  nvm install 24
  nvm alias default 24
  node -v   # should be v24.x
  ```
- **Python 3.11+** with [`uv`](https://docs.astral.sh/uv/) installed.
- **macOS only — `libomp`** is required by XGBoost:
  ```bash
  brew install libomp
  ```
  Without it, the backend crashes on import with `Library not loaded: @rpath/libomp.dylib`.

## 1) Run backend

```bash
cd backend
uv sync                         # installs fastapi, xgboost, pandas, numpy, scikit-learn, etc.
uv run python seed.py           # seeds SQLite with mock items + daily price history
uv run uvicorn app.main:app --reload --port 8000
```

Backend API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

If `uv sync` is slow the first time, that's expected — `xgboost`, `pandas`, and `scipy` together pull ~40 MB of wheels.

## 2) Run frontend

```bash
cd frontend
nvm use 24                      # confirm you're on Node 24, not 25
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend URL: `http://localhost:3000`

If you previously ran the dev server on Node 25 and saw `localStorage` errors, also clear the stale build cache:
```bash
rm -rf .next
```

## 3) Core endpoints

- `GET /health`
- `GET /items?search=&category=&max_price=`
- `GET /items/{id}`
- `GET /items/{id}/history`
- `POST /watchlist`
- `GET /watchlist/{user_tag}`
- `POST /insights/{item_id}` — runs the XGBoost model, returns predicted price, BUY/WAIT advice with confidence, statistics, and top feature importances

## 4) Demo flow

1. Open dashboard and filter by category/budget.
2. Open an item to see price history chart.
3. Set target price in watchlist.
4. Click **Generate** on an item detail page to run the XGBoost model and see the predicted next price, BUY/WAIT recommendation with confidence, supporting signals, and the top features driving the prediction.

## Troubleshooting

- **`localStorage.getItem is not a function`** in `npm run dev` → you're on Node 25. Switch to Node 24 (see Prerequisites) and `rm -rf frontend/.next`.
- **`Library not loaded: @rpath/libomp.dylib`** when starting backend → run `brew install libomp`.
- **Editor warns "Package fastapi is not installed"** → your editor's Python interpreter isn't pointing at `backend/.venv`. Either select that interpreter, or ignore — `uv run` uses the right env.
- **`/insights/{id}` returns 400 "Not enough data"** → the item has fewer than 10 daily price points; reseed or add more snapshots.
