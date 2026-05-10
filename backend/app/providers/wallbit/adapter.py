"""Adapt raw Wallbit responses to flat row dicts the API can return.

Wallbit's exact shapes are not fully documented; we accept several common
shapes and fall back to passing the raw payload through.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _first_present(item: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = item.get(key)
        if value is not None:
            return value
    return None


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


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
        amount = _first_present(it, ("amount", "balance", "available", "value"))
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
        shares = _first_present(it, ("shares", "quantity", "qty"))
        current_price_usd = _first_present(
            it,
            ("current_price_usd", "price_usd", "price", "share_price", "market_price"),
        )
        usd_value = _first_present(it, ("usd_value", "value_usd", "market_value", "value"))
        avg_cost_usd = _first_present(it, ("avg_cost_usd", "average_cost_usd", "avg_price"))
        cost_basis_usd = _first_present(it, ("cost_basis_usd", "cost_basis"))

        shares_float = _to_float(shares)
        price_float = _to_float(current_price_usd)
        avg_cost_float = _to_float(avg_cost_usd)
        if usd_value is None and shares_float is not None and price_float is not None:
            usd_value = shares_float * price_float
        if cost_basis_usd is None and shares_float is not None and avg_cost_float is not None:
            cost_basis_usd = shares_float * avg_cost_float

        rows.append(
            {
                "kind": "stocks",
                "account": "investment",
                "symbol": symbol,
                "shares": shares,
                "usd_value": usd_value,
                "current_price_usd": current_price_usd,
                "avg_cost_usd": avg_cost_usd,
                "cost_basis_usd": cost_basis_usd,
                "raw": it,
            }
        )
    return rows


def asset_to_price_usd(payload: Any) -> float | None:
    body = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload
    if not isinstance(body, dict):
        return None
    return _to_float(
        _first_present(
            body,
            ("price", "current_price", "current_price_usd", "price_usd", "market_price"),
        )
    )


def transaction_cost_basis_by_symbol(payload: Any) -> dict[str, dict[str, float]]:
    items = _ensure_list(payload, ("transactions", "data", "items", "results"))
    totals: dict[str, dict[str, float]] = {}
    latest_prices: dict[str, tuple[datetime | None, float]] = {}
    for it in items:
        if not isinstance(it, dict) or str(it.get("type", "")).upper() != "TRADE":
            continue
        if str(it.get("status", "")).upper() in {"FAILED", "CANCELLED", "CANCELED", "REJECTED"}:
            continue

        trade_info = it.get("trade_info") if isinstance(it.get("trade_info"), dict) else {}
        dest_currency = it.get("dest_currency") if isinstance(it.get("dest_currency"), dict) else {}
        symbol = trade_info.get("symbol") or it.get("symbol") or dest_currency.get("code")
        if not symbol:
            continue
        symbol = str(symbol)

        share_price = _to_float(
            _first_present(trade_info, ("share_price", "price", "price_usd", "current_price_usd"))
        )
        if share_price is not None and share_price > 0:
            occurred_at = _parse_ts(_first_present(it, ("created_at", "timestamp", "date", "ts")))
            latest = latest_prices.get(symbol)
            if latest is None or (
                occurred_at is not None and (latest[0] is None or occurred_at > latest[0])
            ):
                latest_prices[symbol] = (occurred_at, share_price)

        direction = str(trade_info.get("direction") or it.get("direction") or "").upper()
        if direction != "BUY":
            continue

        shares = _to_float(_first_present(it, ("dest_amount", "shares", "quantity", "qty")))
        source_amount = _to_float(_first_present(it, ("source_amount", "amount")))
        if source_amount is None and shares is not None and share_price is not None:
            source_amount = shares * share_price
        if shares is None or shares <= 0 or source_amount is None or source_amount <= 0:
            continue

        row = totals.setdefault(symbol, {"shares": 0.0, "cost_usd": 0.0})
        row["shares"] += shares
        row["cost_usd"] += source_amount

    result = {
        symbol: {
            "avg_cost_usd": values["cost_usd"] / values["shares"],
            "total_bought_shares": values["shares"],
            "total_bought_cost_usd": values["cost_usd"],
        }
        for symbol, values in totals.items()
        if values["shares"] > 0
    }
    for symbol, (_, price) in latest_prices.items():
        result.setdefault(symbol, {})["latest_price_usd"] = price
    return result


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
