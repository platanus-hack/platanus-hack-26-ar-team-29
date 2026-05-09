# Backend Testing — manual recipes

Pure-unit tests run on every developer machine without external services. Anything that touches Postgres, the Fernet vault, or a public Ethereum testnet RPC is gated to skip cleanly when the environment is missing, and is documented here as a manual recipe.

For the locked design see [`02-3` §5.13](../../.claude/artifacts/02-3_api_surface.md#513-custodial-ethereum-wallets-and-defi-aave--morpho).

## What runs in `uv run pytest -q`

| Test file | Needs DB? | Needs `FERNET_KEY`? | Needs RPC? |
|---|---|---|---|
| `test_health.py` | yes | yes | no |
| `test_chat_smoke.py` | yes | yes | no |
| `test_plan_smoke.py` | yes | yes | no |
| `test_ws_smoke.py` | yes | yes | no |
| `test_ethereum_credentials.py` | no | injected per-test | no |
| `test_connections_ethereum_custodial.py` | yes (skips otherwise) | yes (skips otherwise) | no |

The custodial-Ethereum connections file (`test_connections_ethereum_custodial.py`) auto-skips its 7 tests if it cannot open a TCP socket to the Postgres host in `DATABASE_URL` *or* `FERNET_KEY` is unset. To exercise it, follow `backend/README.md`'s quick-start to bring up Postgres + a Fernet key and apply migrations.

## Manual test — custodial Ethereum live RPC

The default suite never hits a live RPC; gas / simulate / transfer paths must be exercised by hand against Sepolia (or another supported testnet). Recipe below uses Sepolia and a faucet-funded EOA.

### Prereqs

1. Backend running locally (`uv run uvicorn app.main:app --port 8000`).
2. A reachable Postgres + applied migrations (`0001_init_mvp` and `0002_ethereum_custodial_constraints`).
3. A funded testnet wallet on the network you'll target. Faucets:
   - Sepolia ETH: <https://sepoliafaucet.com>, <https://www.alchemy.com/faucets/ethereum-sepolia>
   - Sepolia USDC: <https://faucet.circle.com> (mints to your address from Circle)
   - Holesky ETH: <https://holesky-faucet.pk910.de>
   - Polygon Amoy: <https://faucet.polygon.technology>
   - Base Sepolia: <https://www.alchemy.com/faucets/base-sepolia>
   - Arbitrum Sepolia: <https://www.alchemy.com/faucets/arbitrum-sepolia>

### 1. Create or import a wallet

```bash
# Option A: import an existing key
curl -sS -X POST http://localhost:8000/api/v1/connections/ethereum-custodial/import \
  -H 'Content-Type: application/json' \
  -d '{"network":"sepolia","private_key":"0x...","label":"Sepolia demo","primary_asset_hint":"USDC"}'

# Option B: have the server generate one (mnemonic shown ONCE)
curl -sS -X POST http://localhost:8000/api/v1/connections/ethereum-custodial/create \
  -H 'Content-Type: application/json' \
  -d '{"network":"sepolia","label":"Sepolia demo","primary_asset_hint":"USDC"}'
```

Capture `data.id` (`CONN_ID`) and `data.address`. Generated wallets start with 0 ETH — fund them manually from the faucet linked above.

### 2. Gas suggestion

```bash
curl -sS http://localhost:8000/api/v1/connections/$CONN_ID/onchain/gas | jq
```

Expected: `data.tiers.{slow,standard,fast}.gas_price_gwei` populated, `base_gas_price_wei` matching what the RPC reports.

### 3. Simulate a transfer

```bash
curl -sS -X POST http://localhost:8000/api/v1/connections/$CONN_ID/onchain/simulate \
  -H 'Content-Type: application/json' \
  -d '{"asset":"ETH","to":"0xRecipient...","amount":"0.001"}' | jq
```

Expected: `data.ok: true` and a `gas_estimate` near 21000 for ETH (≈ 65k for ERC-20). Insufficient balance returns `ok: false` with a redacted `revert_summary` (no raw revert text leaks).

### 4. Send the transfer

```bash
curl -sS -X POST http://localhost:8000/api/v1/connections/$CONN_ID/onchain/transfer \
  -H 'Content-Type: application/json' \
  -d '{"asset":"ETH","to":"0xRecipient...","amount":"0.001","gas_speed":"standard"}' | jq
```

Expected: `data.tx_hash`, `data.status:"pending"`, `data.block_explorer_url` pointing at the right scanner. Open the URL in a browser to confirm the tx broadcasts.

For an ERC-20 transfer (USDC on Sepolia) replace the body with:

```json
{"asset":"USDC","to":"0x...","amount":"1.00","gas_speed":"standard"}
```

Sepolia is the only network with USDC built in; other networks return `400 ASSET_NOT_SUPPORTED` for now.

### 5. Export the private key

```bash
curl -sS -X POST http://localhost:8000/api/v1/connections/$CONN_ID/export-private-key \
  -H 'Content-Type: application/json' \
  -d '{"confirm":true}' -i
```

Expected: `200 OK`, `Cache-Control: no-store, private`, `data.private_key` is the 0x-hex 32-byte key, `data.warning_es` rendered. Calling on a non-custodial connection returns `400 NOT_EXPORTABLE`.

### Negative paths to spot-check by hand

| Input | Expected status / code |
|---|---|
| `network: "mainnet"` on `/import` or `/create` | `400 NETWORK_NOT_ALLOWED` |
| `private_key: "not a key"` on `/import` | `400 VALIDATION_FAILED` |
| `private_key: "abandon abandon ... abandon"` (12x same word, bad checksum) | `400 VALIDATION_FAILED` |
| `to: "0xnot-an-address"` on `/simulate` or `/transfer` | `400 INVALID_ADDRESS` |
| `asset: "USDT"` on Sepolia | `400 ASSET_NOT_SUPPORTED` |
| Sending more than the wallet holds | `400 INSUFFICIENT_FUNDS` |

## Logs to spot-check

After a successful `/onchain/transfer` you should see exactly one structlog line containing `event=onchain_transfer_broadcast` with the tx hash, network, asset, gas units; no `private_key` or `mnemonic` should appear in any log line.

After a successful `/export-private-key` you should see `event=export_private_key_success`, `success=True`, the connection id, but again no key value.
