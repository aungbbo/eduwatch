# EduWatch Project Presentation (6 Slides)

## Slide 1 - Project Overview
- **Project name:** EduWatch
- **Goal:** Help students save money by tracking prices of study essentials and suggesting when to buy.
- **Problem:** Students usually buy textbooks, stationery, and gadgets without clear price trend visibility.
- **Solution:** A simple web app with a product dashboard, item detail analytics, watchlist, and recommendation endpoint.
- **Current status:** Functional MVP with working frontend + backend + seeded demo data.

## Slide 2 - Product Features (What Users Can Do Now)
- Browse items on the dashboard with search, category filter, and budget filter.
- View each item’s lowest current price and affordability band.
- Open item details to see a historical price chart and trend indicators.
- Add target price to a watchlist (demo user tag: `demo-student`).
- Generate an instant recommendation: buy now vs wait.

## Slide 3 - System Architecture
- **Frontend:** Next.js 15 + React 19 + Tailwind CSS + Recharts.
- **Backend:** FastAPI + SQLAlchemy + Pydantic.
- **Database:** SQLite for local MVP persistence.
- **Data model:** `Item`, `PriceSnapshot`, and `WatchlistEntry`.
- **Communication:** Frontend calls REST endpoints through `frontend/lib/api.ts`.

## Slide 4 - API and Data Flow
- Main endpoints:
  - `GET /items`, `GET /items/{id}`, `GET /items/{id}/history`
  - `POST /watchlist`, `GET /watchlist/{user_tag}`
  - `POST /insights/{item_id}`, `GET /health`
- Data is seeded with realistic multi-day price snapshots for demo items.
- Dashboard -> item detail -> chart -> watchlist/insight forms a complete user journey.
- API docs available through FastAPI Swagger (`/docs`) for quick testing.

## Slide 5 - Current Progress Snapshot
- **Completed**
  - End-to-end MVP flow is implemented and runnable locally.
  - UI has modern dashboard cards, filters, detail view, and charting.
  - Backend supports all core CRUD/read flows needed for demo.
- **In progress / needs hardening**
  - AI insight is rule-based (not yet model-driven intelligence).
  - No authentication yet (uses `user_tag` string).
  - No production deployment, alerting, or test coverage pipeline shown yet.

## Slide 6 - Next Steps and Impact
- Add login + user-specific watchlists.
- Introduce background price monitoring and notifications (email/Telegram/push).
- Improve recommendation quality with richer signals and optional LLM reasoning.
- Add deployment + CI + tests for reliability.
- **Impact vision:** Students make smarter purchase timing decisions and reduce essential study expenses.

---

# 8-Minute Video Shooting Plan

## Suggested Run of Show (8:00 total)
- **0:00-0:45** - Hook and problem statement
  - Talk about student budget pain points.
  - Show one quick statistic or relatable scenario.
- **0:45-1:30** - Introduce EduWatch and value proposition
  - One sentence: "Track prices, set targets, and decide buy-now vs wait."
- **1:30-3:15** - Live demo: dashboard experience
  - Show search + category + max budget filter.
  - Highlight best deal card and item affordability labels.
- **3:15-5:15** - Live demo: item detail and decision support
  - Open one item, explain chart/trend blocks.
  - Add a target price to watchlist.
  - Click "Generate" recommendation and interpret result.
- **5:15-6:30** - Technical architecture walkthrough
  - Show simple diagram: Next.js -> FastAPI -> SQLite.
  - Mention key endpoints and seeded data strategy.
- **6:30-7:30** - Progress, challenges, and learnings
  - What is done, what was hard, what was learned.
- **7:30-8:00** - Roadmap and call to action
  - Next features and expected impact on students.

## Shot Ideas (Practical)
- Use a split: webcam (small corner) + screen capture for product demo.
- Start with one "talking head" intro to build trust, then transition to interface walkthrough.
- During architecture section, show one clean slide/diagram rather than raw code.
- Keep cursor movements deliberate; zoom in browser to 110-125% for readability.
- Use chapter title overlays (Problem, Demo, Tech, Progress, Next).

## Narration Tips
- Keep language outcome-focused ("what student gains") over implementation-heavy details.
- For every feature shown, answer: "Why does this matter to users?"
- Use one concrete user story (e.g., "A student waiting for calculator discount").

## Backup Plan (If Demo Fails Live)
- Pre-record a clean demo run and keep it ready.
- Keep screenshots of key screens (dashboard, detail chart, watchlist success, insight result).
- Continue with architecture + progress slides even if backend/frontend disconnects.

---

# Speaker Script (Slide-by-Slide)

## Slide 1 Script - Project Overview (about 60 seconds)
"Today I am presenting EduWatch, a student-focused price tracking MVP.  
The core problem we address is that students often buy essential items like textbooks, stationery, and gadgets without clear insight into price trends.  
EduWatch helps by showing the best available prices, historical trends, and a quick buy-now or wait recommendation.  
At this stage, we have a functional end-to-end MVP with both frontend and backend running locally."

## Slide 2 Script - Product Features (about 75 seconds)
"On the dashboard, users can search items, filter by category, and set a max budget.  
Each card shows the item, best price, and an affordability indicator.  
When users open an item detail page, they can view historical price movement in a chart.  
They can also set a target price in the watchlist and request an instant recommendation to decide whether to buy now or wait.  
So, the current product already supports a complete decision-making flow."

## Slide 3 Script - Architecture (about 75 seconds)
"The system is split into a modern frontend and lightweight backend.  
Frontend uses Next.js with React and Tailwind, plus Recharts for visualization.  
Backend uses FastAPI with SQLAlchemy and Pydantic.  
For the MVP stage, SQLite is used for simple local persistence.  
The frontend calls backend REST APIs through a dedicated API layer, keeping the architecture clean and easy to scale."

## Slide 4 Script - API and Data Flow (about 80 seconds)
"These are the core endpoints powering the app.  
Items and item details come from read endpoints, watchlist actions are handled through create/read routes, and recommendation comes from an insights endpoint.  
We seed realistic mock data so the dashboard and charts are immediately demo-ready.  
The user journey is straightforward: discover items on dashboard, inspect trend details, set target price, and receive a recommendation."

## Slide 5 Script - Current Progress (about 80 seconds)
"In terms of progress, the MVP foundation is complete: core UI, core APIs, database models, and seeded demo data are all working together.  
What is not yet production-ready is equally important to note.  
The recommendation logic is currently rule-based, authentication is not implemented yet, and deployment plus automated testing pipeline are still pending.  
So this phase proves feasibility and user flow, while the next phase will focus on reliability and intelligence."

## Slide 6 Script - Next Steps and Impact (about 70 seconds)
"Our next steps are to add authentication, personalized watchlists, and automated notifications when prices hit user targets.  
We also plan to strengthen recommendation quality using richer price signals and optional AI-based reasoning.  
With deployment, CI, and tests in place, EduWatch can evolve from MVP to a usable student product.  
The long-term impact is helping students make smarter purchase decisions and reduce education-related costs."

---

# Google Slides Ready Format (Copy/Paste)

## Slide 1 - Project Overview
**Title:** EduWatch: Smart Student Savings Tracker  
**Bullets:**
- Students struggle to know the best time to buy essentials.
- EduWatch tracks item prices and supports smarter purchase timing.
- MVP includes dashboard, item insights, watchlist, and recommendation.
- Current build is functional end-to-end (frontend + backend + data).

## Slide 2 - Features Implemented
**Title:** What Users Can Do Today  
**Bullets:**
- Search and filter items by category and budget.
- View lowest price and affordability labels.
- Open item detail page with historical price chart.
- Save target price to watchlist.
- Generate buy-now vs wait recommendation.

## Slide 3 - Technical Architecture
**Title:** System Design (MVP)  
**Bullets:**
- Frontend: Next.js 15, React 19, Tailwind, Recharts.
- Backend: FastAPI, SQLAlchemy, Pydantic.
- Database: SQLite for local persistence.
- REST API integration through `frontend/lib/api.ts`.

## Slide 4 - API and Product Flow
**Title:** How Data Moves Through EduWatch  
**Bullets:**
- Core endpoints: `/items`, `/items/{id}`, `/watchlist`, `/insights/{item_id}`.
- Seeded dataset provides realistic multi-day price snapshots.
- User flow: dashboard -> detail chart -> target watchlist -> recommendation.
- FastAPI docs at `/docs` support quick testing and validation.

## Slide 5 - Current Progress
**Title:** Progress Update  
**Bullets:**
- End-to-end MVP flow is complete and demo-ready.
- UI and backend APIs are integrated and operational.
- Recommendation logic is currently heuristic/rule-based.
- Authentication, deployment, and automated tests are pending.

## Slide 6 - Roadmap and Expected Impact
**Title:** Next Phase  
**Bullets:**
- Add login and user-specific watchlist management.
- Add notifications when target prices are reached.
- Improve recommendation intelligence with richer signals/AI.
- Deploy with CI/testing for reliability.
- Expected impact: help students reduce essential study expenses.

## Presenter Notes (Optional Footer on Final Slide)
- "EduWatch proves the concept with a working MVP and clear user value."
- "Next milestones focus on production readiness and personalized experience."
