# DeFi endpoints (Phase 2 — Aave V3 supply / withdraw)

Authoritative spec: [`02-3` §5.13.3](../../.claude/artifacts/02-3_api_surface.md#5133-defi-aave-v3--morpho-blue). This page is the backend-side index — local notes only, no contract duplication.

## Status

Phase 2 — Aave V3 only — ships the full §5.13.3 surface:

- `GET /api/v1/defi/markets` — list markets, filters: `protocol`, `network`, `asset`, `min_apy`.
- `GET /api/v1/defi/markets/{protocol}/{market_id}` — market detail.
- `GET /api/v1/connections/{id}/defi/positions` — supplied positions on a custodial Ethereum connection.
- `POST /api/v1/connections/{id}/defi/supply` — approve (if needed) + supply.
- `POST /api/v1/connections/{id}/defi/withdraw` — withdraw a decimal amount or `"max"`.

Morpho Blue is **not** shipped yet. The DefiService is structured so a Morpho adapter slots in alongside Aave with the same response shapes.

## Markets shipped

| Network | Asset | Pool | aToken |
|---|---|---|---|
| `base` (mainnet) | `USDC` | `0xA238Dd80C259a72e81d7e4664a9801593F98d1c5` | `0x4e65fE4DbA92790696d040ac24Aa414708F5c0AB` |

The `base` mainnet allowance is a documented deviation from `02-3` §14 row 28 — see [`deviations.md` §9](./deviations.md). Adding more (network, asset) pairs is a one-row change in [`app/providers/ethereum/aave.py`](../app/providers/ethereum/aave.py).

## File map

| Path | Role |
|---|---|
| `app/providers/ethereum/aave.py` | Aave V3 market registry, ABI fragments, RAY APR → APY conversion |
| `app/providers/ethereum/client.py` | New methods: `aave_get_reserve_data`, `aave_supply`, `aave_withdraw`, `erc20_allowance`, `erc20_approve`, `erc20_total_supply` |
| `app/services/defi.py` | `DefiService` — five ops; two-tx supply (approve when allowance < amount) |
| `app/api/rest/defi.py` | Two routers — `markets_router` mounts under `/defi`, `connection_scoped_router` under `/connections` |
| `app/api/__init__.py` | Wires both routers under `/api/v1` |
| `app/api/deps.py` | `get_defi_service` factory |
| `app/providers/ethereum/capabilities.py` | Capability list extended with `supply_defi`, `withdraw_defi`, `list_defi_markets`, `get_defi_market`, `list_defi_positions` |

## Conventions

- **Approve flow:** `supply` checks allowance; if it's below `amount`, it sends an `approve(uint256.max)` first and includes `approve_tx_hash` in the response. Subsequent supplies for the same `(asset, spender)` skip approve and return `null`. Max approval is intentional — single-shot per pair, lowest gas long-term, the user can revoke from the dashboard if we wire that later.
- **`amount = "max"` on withdraw:** passes `type(uint256).max` to `Pool.withdraw`. Aave V3 reads that as "the caller's full aToken balance" — saves a balanceOf round-trip.
- **USD valuation:** `total_supplied_usd`, `tvl_usd`, `supplied_usd` assume **USDC = $1**. Acceptable since USDC is the only asset shipped. When the registry adds non-stable assets, plug in a price oracle here (a `PriceOracle` capability is the natural shape).
- **APY math:** `currentLiquidityRate` (RAY APR, per Aave V3) → APY via `(1 + apr/SECONDS_PER_YEAR)^SECONDS_PER_YEAR - 1` with `SECONDS_PER_YEAR = 31_536_000` (365 days, no leap). Matches Aave's published frontends.
- **`market_id`:** `aave-v3-{network}-{symbol}` per the artifact. Inverse parse handles dashed network slugs like `base-sepolia` (symbol is the last segment).
- **`position_id`:** `aave-v3-{network}-{symbol}-{address[:10]}` — short, deterministic, unique per (user, market). Not stored in the DB; recomputed on each read.

## Audit / log redaction

Successful writes log:
- `event=defi_supply_broadcast` — connection id, market_id, network, asset, amount, both tx hashes (no key material).
- `event=defi_withdraw_broadcast` — same but `tx_hash` only.

Read failures log `aave_market_read_failed` / `aave_position_read_failed` at `WARN` and skip the row. RPC raw error text is never surfaced in API responses.

## Tests

- [`tests/test_defi_unit.py`](../tests/test_defi_unit.py) — pure-unit (no DB, no RPC): market_id round-trip incl. dashed networks, RAY → APY against known APRs (1%, 5%, 10%), utilization edge cases, ABI shape, amount helper validation.
- Live-RPC flows (read reserve data, supply, withdraw) are out of the default suite; manual recipe is the same shape as the on-chain transfer recipe in [`testing.md`](./testing.md): set `ETHEREUM_RPC_URL_BASE` to a paid provider, fund a small wallet with USDC, hit the routes, watch tx hashes on basescan.

## TODOs left in the code

- **Morpho Blue adapter**: same response shapes; sibling file under `app/providers/ethereum/` once we pick a market.
- **Price oracle capability**: stop assuming USDC = $1 once non-stable assets land in the registry.
- **WebSocket position-update frames**: `connection.<id>` should emit a `position_updated` after a successful supply/withdraw. The connection topic doesn't exist yet (also pending for the Phase 1 transfer flow); land both at once.
- **Audit log**: the broader `audit_log_entries` table is deferred (`deviations.md` §3); when it lands, write supply/withdraw entries with tx hashes redacted only for failures, not successes.
