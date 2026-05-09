# Custodial Ethereum endpoints (Phase 1)

Authoritative spec: [`02-3` §5.13](../../.claude/artifacts/02-3_api_surface.md#513-custodial-ethereum-wallets-and-defi-aave--morpho). This page is a backend-side index; it does not duplicate the contract.

## Status

Phase 1 (this pass) ships:

- `POST /api/v1/connections/ethereum-custodial/import` — accepts a 0x-hex 32-byte private key OR a 12/24-word BIP-39 mnemonic.
- `POST /api/v1/connections/ethereum-custodial/create` — server-generates a keypair; mnemonic returned **once** in the response, never again.
- `GET  /api/v1/connections/{id}/onchain/gas`
- `POST /api/v1/connections/{id}/onchain/simulate`
- `POST /api/v1/connections/{id}/onchain/transfer`
- `POST /api/v1/connections/{id}/export-private-key` (`chat_excluded` per `02-3` §14 row 31).

Phase 2 (deferred): `/defi/markets`, `/connections/{id}/defi/positions`, `/connections/{id}/defi/{supply,withdraw}`. The package is structured so these drop in without further refactor.

## Networks

Locked allowlist (testnets only — `02-3` §14 row 28):
`sepolia`, `holesky`, `polygon-amoy`, `arbitrum-sepolia`, `base-sepolia`. Mainnet slugs return `400 NETWORK_NOT_ALLOWED`.

Per-network metadata (`chain_id`, explorer template, known ERC-20 contract addresses) lives in [`app/providers/ethereum/networks.py`](../app/providers/ethereum/networks.py).

USDC is shipped on every supported network *except* Holesky (Circle has no Holesky deployment at the time of writing). USDT testnet support is intentionally not shipped; requesting USDT returns `400 ASSET_NOT_SUPPORTED`.

## Per-network RPC config

Replace the previous single `ETHEREUM_RPC_URL` env var with five per-network ones:

```text
ETHEREUM_RPC_URL_SEPOLIA
ETHEREUM_RPC_URL_HOLESKY
ETHEREUM_RPC_URL_POLYGON_AMOY
ETHEREUM_RPC_URL_ARBITRUM_SEPOLIA
ETHEREUM_RPC_URL_BASE_SEPOLIA
```

Defaults are public publicnode endpoints; override for prod-grade reliability.

## File map

| Path | Role |
|---|---|
| `app/providers/ethereum/auth.py` | `EthereumCustodialCredentials` dataclass + Fernet blob helpers (mirrors `wallbit/auth.py`) |
| `app/providers/ethereum/networks.py` | Network registry: chain_id, explorer URL, known ERC-20 contracts |
| `app/providers/ethereum/abi.py` | Minimal ERC-20 ABI (`balanceOf` / `decimals` / `symbol` / `transfer`) |
| `app/providers/ethereum/client.py` | Sync web3.py wrapper exposed as async via `asyncio.to_thread`. One `Web3` per network, cached |
| `app/providers/ethereum/capabilities.py` | `EthereumCustodialProvider(Provider)` with Phase 1 capabilities |
| `app/providers/ethereum/adapter.py` | Placeholder for Phase 2 response normalization |
| `app/services/connections.py` | Adds `import_ethereum_custodial`, `create_ethereum_custodial`, `export_private_key`, `get_active_ethereum_custodial` |
| `app/services/onchain.py` | `OnchainService` — gas suggestion, simulate, transfer (ETH + ERC-20) |
| `app/api/rest/connections.py` | Adds the three connection-management routes + the export endpoint |
| `app/api/rest/onchain.py` | Adds the `/onchain/{gas,simulate,transfer}` routes |
| `alembic/versions/0002_ethereum_custodial_constraints.py` | Adds `ethereum_custodial` to `connection_type` and `private_key` to `auth_kind` |

## Audit / log redaction

The service layer never logs `private_key` or `mnemonic`. Successful calls log:

- `event=ethereum_custodial_imported` — connection id, network, address.
- `event=ethereum_custodial_created` — connection id, network, address. (Mnemonic never logged; only returned in the response body.)
- `event=onchain_transfer_broadcast` — connection id, network, asset, tx hash, gas units, gas speed.
- `event=export_private_key_success` — connection id, `success=true`, `tool="export_private_key"`. Key value never logged.

There is no `audit_log_entries` table in the MVP yet (deferred per `docs/deviations.md` §3); when it lands, the export endpoint must redact the `private_key` field.

## TODOs left in the code

- **Rate-limit on `/export-private-key`** (max 5/hour per `02-3` §5.13.5). Marked `TODO(phase-1.1)` in `app/api/rest/connections.py`. Wire when the rate-limiter middleware lands.
- **WebSocket transfer status** on `connection.<id>` topic (`02-3` §5.13.2). Topic doesn't exist yet; `app/services/onchain.py` carries a `TODO(phase-1.1)` comment at the broadcast site.
- **Re-auth before export** (`02-3` §16 q17, deferred). v1 trusts the bearer token.

## Tests

- `tests/test_ethereum_credentials.py` — pure-unit (no DB, no RPC). Round-trip encryption, address derivation from a known hex key, mnemonic derivation against the canonical "abandon abandon … about" vector, input-shape detection edge cases.
- `tests/test_connections_ethereum_custodial.py` — REST shape against the live FastAPI app + Postgres. Auto-skips if the DB or `FERNET_KEY` isn't reachable; CI must bring up Postgres + run migrations + set `FERNET_KEY` for these to execute.
- Live-RPC flows (gas, simulate, transfer) are out of the default suite; see [`testing.md`](./testing.md) for the manual recipe.
