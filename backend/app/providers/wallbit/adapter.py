"""Adapt raw Wallbit responses to flat row dicts the API can return.

Wallbit's exact shapes are not fully documented; we accept several common
shapes and fall back to passing the raw payload through.
"""

from __future__ import annotations

from typing import Any


def _ensure_list(payload: Any, key_candidates: tuple[str, ...] = ()) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if (
            "data" in payload
            and isinstance(payload["data"], dict)
            and "data" in payload["data"]
            and isinstance(payload["data"]["data"], list)
        ):
            return payload["data"]["data"]
        for k in key_candidates:
            if k in payload and isinstance(payload[k], list):
                return payload[k]
        # Otherwise the dict itself is one row.
        return [payload]
    return []


def checking_balance_to_rows(payload: Any) -> list[dict[str, Any]]:
    items = _ensure_list(payload, ("balances", "data", "items", "results"))
    rows: list[dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        currency = it.get("currency") or it.get("symbol") or it.get("ccy") or "USD"
        amount = it.get("amount") or it.get("balance") or it.get("available") or it.get("value")
        rows.append(
            {
                "kind": "checking",
                "account": "checking",
                "symbol": currency,
                "currency": currency,
                "amount": amount,
                "raw": it,
            }
        )
    return rows


def stocks_balance_to_rows(payload: Any) -> list[dict[str, Any]]:
    items = _ensure_list(payload, ("positions", "stocks", "data", "items", "results"))
    rows: list[dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        symbol = it.get("symbol") or it.get("ticker") or it.get("asset")
        shares = it.get("shares") or it.get("quantity") or it.get("qty")
        usd_value = (
            it.get("usd_value") or it.get("value_usd") or it.get("market_value") or it.get("value")
        )
        rows.append(
            {
                "kind": "stocks",
                "account": "investment",
                "symbol": symbol,
                "shares": shares,
                "usd_value": usd_value,
                "raw": it,
            }
        )
    return rows


def transactions_to_rows(payload: Any) -> list[dict[str, Any]]:
    items = _ensure_list(payload, ("transactions", "data", "items", "results"))
    rows: list[dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        currency = it.get("currency") or it.get("ccy") or it.get("symbol")
        if not currency and "source_currency" in it and isinstance(it["source_currency"], dict):
            currency = it["source_currency"].get("code")

        amount = it.get("amount") or it.get("source_amount") or it.get("value")

        desc = it.get("description") or it.get("memo") or it.get("comment")
        if not desc and "trade_info" in it and isinstance(it["trade_info"], dict):
            direction = it["trade_info"].get("direction", "")
            symbol = it["trade_info"].get("symbol", "")
            desc = f"{direction} {symbol}".strip()

        rows.append(
            {
                "id": it.get("id") or it.get("transaction_id") or it.get("uuid"),
                "type": it.get("type") or it.get("kind") or it.get("category"),
                "status": it.get("status") or it.get("state"),
                "amount": amount,
                "currency": currency,
                "created_at": (
                    it.get("created_at") or it.get("timestamp") or it.get("date") or it.get("ts")
                ),
                "description": desc,
                "raw": it,
            }
        )
    return rows
