# Ledgerly

A clean, personal expense tracker with receipt uploads, budgets and spending insights.

**Stack:** FastAPI + React | **Status:** Phase 5 — React frontend complete

## Quickstart (Phase 1)

```bash
cp backend/.env.example backend/.env
docker compose up
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/v1/health

## What's done

- [x] Monorepo layout (`backend/`, `frontend/`)
- [x] Docker Compose: API + Postgres
- [x] FastAPI app factory (`app/main.py`) with CORS
- [x] Settings via `pydantic-settings` (`app/core/config.py`)
- [x] SQLAlchemy engine + session dependency (`app/core/db.py`)
- [x] Alembic wired to app settings, first empty migration applied
- [x] Ruff + Black + pre-commit hooks
- [x] GitHub Actions CI (lint + test, spins up Postgres service)
- [x] `GET /v1/health` route with a passing test
- [x] `User` and `RefreshToken` models + migration
- [x] `POST /v1/auth/signup` (bcrypt-hashed passwords, 409 on duplicate email)
- [x] `POST /v1/auth/login` (returns 15-min access token + 7-day refresh token)
- [x] `POST /v1/auth/refresh` (rotates refresh tokens; reuse of an old one is rejected)
- [x] `GET /v1/me` protected by `get_current_user`
- [x] 9 passing tests covering signup, login, expired tokens, and refresh rotation
- [x] `Category`, `Expense`, `Budget` models + migrations
- [x] 8 default categories seeded on every signup (Food, Travel, Rent, etc.)
- [x] Full expense CRUD, scoped to the current user (404, never 403, for other users' data)
- [x] Expense filtering (category, date range, amount range), sorting, and pagination
- [x] Receipt upload (`POST /v1/expenses/{id}/receipt`) with MIME/size validation, stored locally in dev
- [x] Budget upsert per category/month (`PUT /v1/budgets`)
- [x] `GET /v1/summary` — spend vs budget by category for a given month
- [x] `GET /v1/summary/trend` — last 6 months of spending
- [x] `GET /v1/expenses/export` — CSV download via `StreamingResponse`
- [x] 22 total passing tests, including cross-user isolation and a hand-calculated summary fixture

**Note on bcrypt version:** `passlib==1.7.4` is incompatible with `bcrypt>=4.1` (a known
upstream bug). This project pins `bcrypt==4.0.1` in `requirements.txt` — don't let it
auto-upgrade.

**Note on Python version:** the project plan targets Python 3.12, but this codebase is
currently kept compatible with **Python 3.9** too (`Optional[X]` instead of `X | None`,
`timezone.utc` instead of `datetime.UTC`) because that's what's installed in local dev.
`pyproject.toml`'s `[tool.ruff] target-version` is pinned to `"py39"` on purpose — **do not
run `ruff check . --fix` and accept 3.10+/3.11+ syntax suggestions** (`UP007`, `UP017`,
`UP045`) without first either bumping this pin intentionally or confirming the deploy
target has actually moved to 3.12.

## Trying the auth endpoints

```bash
# Sign up
curl -X POST http://localhost:8000/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"a-strong-password","name":"You"}'

# Log in — copy the access_token from the response
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"a-strong-password"}'

# Call a protected route
curl http://localhost:8000/v1/me -H "Authorization: Bearer <access_token>"

# Refresh (rotates — the old refresh_token becomes invalid)
curl -X POST http://localhost:8000/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

Or just use `/docs` — click "Authorize" and paste in the access token.

## Local dev without Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at a local Postgres, or use SQLite for quick tests
uvicorn app.main:app --reload
```

## Running migrations

```bash
cd backend
alembic upgrade head          # apply migrations
alembic revision --autogenerate -m "add user model"   # once models exist
```

## Running tests

```bash
cd backend
pytest -v
```

## Trying the Phase 3/4 endpoints

```bash
# List your categories (seeded automatically on signup)
curl http://localhost:8000/v1/categories -H "Authorization: Bearer <access_token>"

# Add an expense
curl -X POST http://localhost:8000/v1/expenses \
  -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" \
  -d '{"category_id":"<category_id>","amount":"42.50","spent_on":"2026-09-15","note":"lunch"}'

# Set a budget for a category/month
curl -X PUT http://localhost:8000/v1/budgets \
  -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" \
  -d '{"category_id":"<category_id>","month":"2026-09","limit_amount":"5000.00"}'

# Spend-vs-budget summary for that month
curl "http://localhost:8000/v1/summary?month=2026-09" -H "Authorization: Bearer <access_token>"

# Upload a receipt
curl -X POST http://localhost:8000/v1/expenses/<expense_id>/receipt \
  -H "Authorization: Bearer <access_token>" -F "file=@receipt.jpg"
```

Receipts are saved under `backend/uploads/` in dev (gitignored) — swap `app/services/storage_service.py`'s
implementation for an S3/R2 client when deploying, per the plan's tech stack.

## Frontend (Phase 5)

- [x] Vite + React + TypeScript, Tailwind CSS with a custom ledger-themed design system
- [x] Axios instance with a 401 → silent refresh → retry interceptor (`src/lib/api.ts`)
- [x] Pages: Login, Signup, Dashboard, Expenses (filter/sort/paginate), Budgets, Settings
- [x] TanStack Query hooks per resource; mutations invalidate expenses/summary/trend together
- [x] Add/Edit expense modal — React Hook Form + Zod, inline receipt upload
- [x] Dashboard: category pie chart + 6-month trend (Recharts), budget bars (amber at 75%, red at 90%, per spec)
- [x] CSV export triggers an authenticated download (not a plain link, since the endpoint needs a Bearer token)
- [x] Empty states on every list/chart, per the plan's UX requirements
- [x] Verified: `npm run build` (`tsc -b && vite build`) passes clean, 0 errors

### Running the frontend

```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:8000/v1, matching the backend
npm run dev             # http://localhost:5173
```

Make sure the backend is running first (`uvicorn app.main:app --reload` from `backend/`).

**Gotcha to know about:** `tsconfig.node.json` (which type-checks `vite.config.ts`) is a
TypeScript *project reference*, and project references are not allowed to set `noEmit` —
they intentionally emit `.d.ts`/`.js` output for other projects to consume. Its `outDir` is
deliberately pointed at `node_modules/.tsc-out/` so that output never lands next to
`vite.config.ts` itself. **Don't remove or repoint that `outDir`** — if `tsc -b` ever emits
a `vite.config.js` next to `vite.config.ts`, Vite will silently load the stale compiled
`.js` version instead of the real `.ts` source, and alias imports (`@/...`) will fail to
resolve in `vite build` with no obvious cause. If you ever see that happen again: delete
any stray `vite.config.js` / `vite.config.d.ts` next to `vite.config.ts` and rebuild.

## Next: Phase 6 — Polish and deploy

- Consistent error format from the API, toast notifications in the UI
- Deploy API + Postgres to Render/Railway, frontend to Vercel; configure CORS and env vars
- README with screenshots, architecture diagram, live demo account

See the full project plan for Phase 6.
