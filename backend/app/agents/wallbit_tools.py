from __future__ import annotations

from typing import Any

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool

from app.config import get_settings


def wallbit_mcp_server():
    return create_sdk_mcp_server(
        name="wallbit",
        version="0.1.0",
        tools=[
            get_checking_balance,
            get_stocks_balance,
            list_transactions,
            get_asset,
            create_trade,
        ],
    )


async def _request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            method,
            f"{settings.wallbit_base_url}{path}",
            headers={"X-API-Key": settings.wallbit_api_key},
            params={k: v for k, v in (params or {}).items() if v is not None},
            json=json,
        )

    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}

    if response.is_error:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Wallbit API error {response.status_code}: {payload}",
                }
            ],
            "is_error": True,
        }

    return {"content": [{"type": "text", "text": str(payload)}], "data": payload}


@tool(
    "get_checking_balance",
    "Obtiene el balance de la cuenta checking del usuario.",
    {},
)
async def get_checking_balance(args: dict[str, Any]) -> dict[str, Any]:
    del args
    return await _request("GET", "/api/public/v1/balance/checking")


@tool(
    "get_stocks_balance",
    "Obtiene el balance de stocks del usuario.",
    {},
)
async def get_stocks_balance(args: dict[str, Any]) -> dict[str, Any]:
    del args
    return await _request("GET", "/api/public/v1/balance/stocks")


@tool(
    "list_transactions",
    "Lista las transacciones del usuario con paginacion.",
    {"type": "object", "properties": {}, "additionalProperties": True},
)
async def list_transactions(args: dict[str, Any]) -> dict[str, Any]:
    return await _request("GET", "/api/public/v1/transactions", params=args)


@tool(
    "get_asset",
    "Obtiene informacion de un asset por su simbolo.",
    {
        "type": "object",
        "properties": {"symbol": {"type": "string"}},
        "required": ["symbol"],
        "additionalProperties": False,
    },
)
async def get_asset(args: dict[str, Any]) -> dict[str, Any]:
    symbol = str(args["symbol"]).upper()
    return await _request("GET", f"/api/public/v1/assets/{symbol}")


@tool(
    "create_trade",
    "Crea una orden de compra o venta de un asset. Requiere aprobacion humana.",
    {
        "type": "object",
        "properties": {
            "symbol": {"type": "string"},
            "direction": {"type": "string", "enum": ["BUY", "SELL", "buy", "sell"]},
            "order_type": {
                "type": "string",
                "enum": ["MARKET", "LIMIT", "market", "limit"],
            },
            "amount": {"type": "number"},
            "shares": {"type": "number"},
            "currency": {"type": "string", "default": "USD"},
        },
        "required": ["symbol", "direction", "order_type"],
        "additionalProperties": False,
    },
)
async def create_trade(args: dict[str, Any]) -> dict[str, Any]:
    payload = {k: v for k, v in args.items() if v is not None}
    payload["symbol"] = str(payload["symbol"]).upper()
    payload["direction"] = str(payload["direction"]).upper()
    payload["order_type"] = str(payload["order_type"]).upper()
    payload["currency"] = str(payload.get("currency", "USD")).upper()
    return await _request("POST", "/api/public/v1/trades", json=payload)
