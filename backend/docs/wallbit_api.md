# Wallbit API Integration

This document serves as the operational contract for the Wallbit DEV API surface as actually observed during integration, rather than what is strictly written in their high-level documentation. The discrepancies and required shapes are documented here to prevent regressions.

**DEV Environment URL:** `https://api.dev.wallbit.io`

**Required Headers (All Requests):**
- `X-API-Key: <your-api-key>`
- `Accept: application/json`

---

## 1. Get Checking Balance
**Endpoint:** `GET /api/public/v1/balance/checking`

**Expected Response Shape:**
```json
{
  "data": [
    {
      "currency": "USD",
      "balance": 19008.2
    }
  ]
}
```
**Adapter Note:** Maps `currency` to `symbol` and `balance` to `amount`.

---

## 2. Get Stocks Balance (Investment Portfolio)
**Endpoint:** `GET /api/public/v1/balance/stocks`

**Expected Response Shape:**
```json
{
  "data": [
    {
      "symbol": "AAPL",
      "shares": 0.56406638
    },
    {
      "symbol": "TSLA",
      "shares": 2.81294465
    }
  ]
}
```
**Adapter Note:** Extracts `symbol` and `shares`. Fiat representation relies on fetching the current price or relying on Wallbit to optionally return a value field.

The `/api/v1/positions` demo endpoint intentionally avoids one `/assets/{symbol}` call per holding to stay under Wallbit rate limits. It uses only `/balance/stocks` plus `/transactions`: the latest `trade_info.share_price` is used as the displayed/fallback price, and historical BUY trades compute best-effort cost basis/P&L. Failed/cancelled/rejected trades are ignored.

---

## 2.1 Get Asset Price
**Endpoint:** `GET /api/public/v1/assets/{symbol}`

**Expected Response Shape:**
```json
{
  "data": {
    "symbol": "AAPL",
    "price": 293.85
  }
}
```

**Adapter Note:** `price`, `current_price`, `current_price_usd`, `price_usd`, and `market_price` are accepted as aliases because the DEV payload shape has varied during the hackathon.

---

## 3. List Transactions
**Endpoint:** `GET /api/public/v1/transactions`
*(Note: Adding query parameters like `?limit=5` might result in `The selected limit is invalid` error depending on backend constraints. Tested without limit successfully).*

**Observed Response Shape (Deeply Nested Data):**
```json
{
  "data": {
    "data": [
      {
        "uuid": "b155570c-7a74-4321-8e3f-6a905aa8ab35",
        "type": "TRADE",
        "source_currency": { "code": "USD", "alias": "USD" },
        "dest_currency": { "code": "AAPL", "alias": "AAPL" },
        "trade_info": {
          "direction": "BUY",
          "symbol": "AAPL",
          "order_type": "MARKET",
          "share_price": 293.85
        },
        "source_amount": 10,
        "dest_amount": 0.03,
        "status": "PENDING",
        "created_at": "2026-05-09T14:51:35.000000Z"
      },
      {
        "uuid": "56126db8-6d12-4cd6-88dd-fb46de72e1be",
        "type": "INVESTMENT_DEPOSIT",
        "source_currency": { "code": "USD", "alias": "USD" },
        "dest_currency": { "code": "USD", "alias": "USD" },
        "source_amount": 10.01,
        "dest_amount": 10.01,
        "status": "COMPLETED",
        "created_at": "2026-05-09T15:01:33.000000Z"
      }
    ],
    "pages": 35,
    "current_page": 1,
    "count": 347
  }
}
```

**Adapter Mapping Logic:**
- List is extracted from `payload["data"]["data"]`.
- `id` maps to `uuid`.
- `amount` maps to `source_amount`.
- `currency` maps to `source_currency.code`.
- `description` auto-generates using `trade_info.direction` + `trade_info.symbol` (e.g. "BUY AAPL") for trades, as `comment` is typically `null`.

---

## 4. Place Trade
**Endpoint:** `POST /api/public/v1/trades`

**Required Headers:**
- `Content-Type: application/json`

**Required Payload Structure:**
The API is strict about field names. Omitting `currency` or using wrong keys like `amount_usd` or `side` will result in HTTP 400 validation errors.

```json
{
  "symbol": "AAPL",
  "direction": "BUY",       // REQUIRED: Must be 'direction', not 'side'
  "order_type": "MARKET",   // REQUIRED: Must be 'order_type', not 'type'
  "currency": "USD",        // REQUIRED: Even if implied by balance
  "amount": 10              // Required when 'shares' is not present
}
```

**Expected Success Response:**
```json
{
  "data": {
    "symbol": "AAPL",
    "direction": "BUY",
    "amount": 10,
    "shares": 0.034029868,
    "status": "REQUESTED",
    "order_type": "MARKET",
    "time_in_force": "DAY",
    "created_at": "2026-05-09T17:19:02.000000Z",
    "updated_at": "2026-05-09T17:19:02.000000Z"
  }
}
```

**Error Handling Note:**
Validation errors return `400 Bad Request` with an `errors` object. Example:
```json
{
  "message": "The direction field is required.",
  "errors": {
    "direction": ["The direction field is required."]
  }
}
```
