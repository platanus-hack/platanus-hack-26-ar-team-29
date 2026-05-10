# 03_build_log.md

## Completed Work
- Designed and implemented the unified transaction database (`canonical_transactions`, `canonical_accounts`, `canonical_assets`, `user_profiles`, etc.) in SQLAlchemy and deployed via Alembic.
- Implemented a Wallbit Ingestion Pipeline (`services/ingestion.py`) that polls `/api/public/v1/transactions`, normalizes the payload, and performs deduplicated upserts into the canonical ledger.
- Implemented the `ClassifierAgent` using Anthropic Claude to analyze batched unclassified transactions, returning structured output with taxonomy categories (`income`, `risky_investment`, `necessary_expense`, etc.) and cleaned-up merchants.
- Added a `ContextService` that recalculates `user_profiles.summaries` (income, expenses, savings rate) based on the classified transaction data.
- Refactored `PortfolioService.read_transactions` to fetch from the canonical database instead of directly querying the Wallbit API.
- Integrated the Next.js frontend `ActivityPage` (`app/activity/page.tsx`) to pull and render the categorized transactions, removing the static mock data.

## Files Changed
- `backend/app/persistence/models/ledger.py` (New)
- `backend/app/persistence/models/users.py` (Added `UserProfile`)
- `backend/alembic/versions/774f440cf2aa_add_ledger_models_and_userprofile.py` (New)
- `backend/app/services/ingestion.py` (New)
- `backend/app/workers/ingest_wallbit.py` (New)
- `backend/app/agents/classifier_agent.py` (New)
- `backend/app/workers/classifier_worker.py` (New)
- `backend/app/services/context.py` (New)
- `backend/app/workers/context_worker.py` (New)
- `backend/app/services/portfolio.py` (Modified `read_transactions`)
- `frontend/app/activity/page.tsx` (Modified to use real API endpoint)

## Commands Run
- Generated migrations: `uv run alembic revision --autogenerate -m "Add ledger models and UserProfile"`
- Applied migrations: `uv run alembic upgrade head`
- Tested Wallbit fetch: `uv run python test_wallbit.py`
- Seeded dev user: `uv run python seed_wallbit_dev.py`
- Ingestion worker: `PYTHONPATH=. uv run python app/workers/ingest_wallbit.py`
- Classifier worker: `PYTHONPATH=. uv run python app/workers/classifier_worker.py`
- Context worker: `PYTHONPATH=. uv run python app/workers/context_worker.py`
- Verification script: `uv run python check_txs.py`
- Backend API server test: `uv run uvicorn app.main:app --port 8001`

## Tests and Results
- Tested the Wallbit API client successfully grabbing `TSLA`, `AMZN`, `AAPL` trades and internal transfers.
- The normalizer correctly mapped `INVESTMENT_DEPOSIT` to `transfer_internal` and `TRADE` to `trade`.
- The Classifier Agent effectively correctly categorized `TSLA` and `AMZN` as `risky_investment` and cleaned up the `merchant` strings to plain "Tesla" and "Amazon". It categorized internal transfers accurately as `transfer`.
- Profile aggregates recalculated cleanly via `ContextService`.
- Re-running the poller showed 0 dupes due to the `on_conflict_do_update` using `(connection_id, external_id)`.

## Env Vars Needed
- `WALLBIT_API_KEY` (existing, tested)
- `WALLBIT_MCP_URL` (existing, fallback defaults implemented)
- `ANTHROPIC_API_KEY` (existing, tested for classification)
- `FERNET_KEY` (existing, credential encryption works)

## API / Deploy Setup Notes
- The Next.js frontend fetches the `/api/v1/transactions` endpoint securely. The frontend defaults to `http://localhost:8000` via `NEXT_PUBLIC_API_URL` which easily maps to the backend server.
- Added a `DEV_USER_ID` override script (`seed_wallbit_dev.py`) to align the DB seeding with the auth mock in `deps.py`.

## Decisions and Shortcuts
- The poller, classifier, and context recalculator are currently implemented as explicit script modules inside `workers/`. In a future iteration or production system, these should be bound to a task scheduler like Celery/ARQ, or scheduled cronjobs.
- The `ContextService` recalculates the summary metrics blindly for all time right now instead of bucketing strictly by current month. Perfect for the MVP horizon.

## Known Issues
- Currently, Wallbit's API has a bug/feature where `/transactions` API does not explicitly paginate with limits cleanly in all cases (422 Invalid Limit error when limit=5 was used). Omitting the limit parameter fetches the entire sequence fine.

## Demo URL
- Available via `http://localhost:3000/activity` when frontend and backend spin up simultaneously.

## Next Steps for Reviewer
- You can spin up both the backend `uvicorn` and frontend Next.js dev server.
- Review the `Activity` tab to see the unified ledger populated directly from Wallbit and magically categorized by Claude.
- We can now link this up to the Chat Agent, which can query these aggregates directly from the `UserProfile` to provide context-aware insights.

## Persistent Database Fix
### Completed Work
- Modified `docker-compose.yml` to use a local host directory (`./.postgres_data`) for the PostgreSQL database volume instead of an ephemeral named volume.
- Added `.postgres_data/` to `.gitignore`.

### Files Changed
- `docker-compose.yml`
- `.gitignore`

### Decisions and Shortcuts
- By mapping the volume to `./.postgres_data`, the database persists fully across `docker compose down -v` or standard `docker compose down` operations. PostgreSQL's Docker entrypoint automatically fixes permissions on the host directory when the container starts.

## Wallbit Investment Tab Enrichment
### Completed Work
- Enriched `/api/v1/positions` to consume Wallbit `/assets/{symbol}` for live prices after reading `/balance/stocks`.
- Added best-effort cost basis and unrealized P&L calculation from Wallbit BUY trades returned by `/transactions`.
- Updated the frontend Investments tab to replace placeholder total value/P&L/risk fields with backend-provided Wallbit data and visible error states.

### Files Changed
- `backend/app/providers/wallbit/adapter.py`
- `backend/app/providers/wallbit/client.py`
- `backend/app/canonical/models.py`
- `backend/app/services/portfolio.py`
- `backend/docs/wallbit_api.md`
- `backend/tests/test_wallbit_adapter.py`
- `frontend/app/lib/backend/types.ts`
- `frontend/app/investments/page.tsx`

### Tests and Results
- Added adapter unit coverage for Wallbit asset price extraction, inline stock valuation, and BUY-trade cost basis calculation.
- `uv run pytest tests/test_wallbit_adapter.py -q` passed: 3 tests.
- `uv run ruff check app/providers/wallbit/adapter.py app/providers/wallbit/client.py app/canonical/models.py app/services/portfolio.py tests/test_wallbit_adapter.py` passed.
- `npx eslint app/investments/page.tsx app/lib/backend/types.ts` passed.
- `npx tsc --noEmit` passed.
- Full backend `uv run pytest -q` is still blocked by pre-existing `ModuleNotFoundError: app.agents.approval` during `tests/test_agent_approval.py` collection.
- Full backend `uv run ruff check app tests/test_wallbit_adapter.py` is still blocked by pre-existing lint issues in unrelated agent/worker files.

### Follow-up Fix
- Added a fallback price source for the Investments tab: when Wallbit `/assets/{symbol}` does not return price data, `/api/v1/positions` now uses the latest `trade_info.share_price` observed in Wallbit transactions.
- Adjusted the Investments UI so missing valuation displays as `n/d` instead of misleading `0.0%` allocation or `$0` totals.
- Inspected live Wallbit `/transactions`: trade rows include `source_amount`, `dest_amount`, `trade_info.symbol`, and `trade_info.share_price`; failed trades are present too, so the adapter now ignores failed/cancelled/rejected trades when calculating cost basis and fallback prices.
