from __future__ import annotations

import json
from typing import Any

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool

BACKEND_BASE = "http://127.0.0.1:8000"


def defi_mcp_server():
    return create_sdk_mcp_server(
        name="defi",
        version="0.1.0",
        tools=[
            list_markets,
            get_market,
            list_positions,
            supply,
            withdraw,
        ],
    )


async def _request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.request(
            method,
            f"{BACKEND_BASE}{path}",
            params={k: v for k, v in (params or {}).items() if v is not None},
            json=json_body,
        )
    try:
        payload = resp.json()
    except ValueError:
        payload = {"raw": resp.text}
    if resp.is_error:
        return {
            "content": [{"type": "text", "text": f"DeFi API error {resp.status_code}: {payload}"}],
            "is_error": True,
        }
    return {"content": [{"type": "text", "text": json.dumps(payload)}], "data": payload}


async def _resolve_eth_connection_id() -> str | None:
    """Find the user's first active ethereum_custodial connection.

    Returns None if the user has no usable ETH wallet — caller surfaces that to
    the agent as a tool error so it can ask the user to create/import one.
    """
    res = await _request("GET", "/api/v1/connections")
    if res.get("is_error"):
        return None
    payload = res.get("data") or {}
    conns = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload
    if not isinstance(conns, list):
        return None
    for c in conns:
        if not isinstance(c, dict):
            continue
        if c.get("connection_type") == "ethereum_custodial" and c.get("status") == "healthy":
            cid = c.get("id")
            if isinstance(cid, str):
                return cid
    return None


_NO_WALLET_RESPONSE = {
    "content": [
        {
            "type": "text",
            "text": (
                "El usuario todavia no tiene una billetera de Ethereum activa. "
                "Pidile que cree o importe una primero usando "
                "mcp__ethereum__create_ethereum_wallet o mcp__ethereum__import_ethereum_wallet."
            ),
        }
    ],
    "is_error": True,
}


@tool(
    "list_markets",
    "Lista mercados de DeFi (Aave V3) disponibles para invertir/generar yield. "
    "Devuelve por cada mercado: protocol, market_id, asset, network, supply_apy, "
    "borrow_apy, total_supplied_usd, utilization, tvl_usd. Esta tool es de solo "
    "lectura y no requiere aprobacion.",
    {
        "type": "object",
        "properties": {
            "asset": {
                "type": "string",
                "description": "Filtrar por simbolo del asset, e.g. USDC.",
            },
            "network": {
                "type": "string",
                "description": "Filtrar por red, e.g. base, sepolia.",
            },
            "min_apy": {
                "type": "number",
                "description": "APY minimo (0 a 1, e.g. 0.04 = 4%).",
            },
        },
        "additionalProperties": False,
    },
)
async def list_markets(args: dict[str, Any]) -> dict[str, Any]:
    params: dict[str, Any] = {"protocol": "aave"}
    for k in ("asset", "network", "min_apy"):
        if args.get(k) is not None:
            params[k] = args[k]
    return await _request("GET", "/api/v1/defi/markets", params=params)


@tool(
    "get_market",
    "Obtiene detalles de un mercado especifico de Aave V3. market_id tiene formato "
    "'aave-v3-<network>-<asset>', e.g. 'aave-v3-base-USDC'.",
    {
        "type": "object",
        "properties": {
            "market_id": {
                "type": "string",
                "description": "ID del mercado, e.g. aave-v3-base-USDC.",
            },
        },
        "required": ["market_id"],
        "additionalProperties": False,
    },
)
async def get_market(args: dict[str, Any]) -> dict[str, Any]:
    market_id = str(args["market_id"])
    return await _request("GET", f"/api/v1/defi/markets/aave/{market_id}")


@tool(
    "list_positions",
    "Lista las posiciones DeFi del usuario en Aave V3 (lo que tiene depositado). "
    "Por cada posicion devuelve: position_id, market_id, asset, supplied_amount, "
    "supplied_usd, supply_apy, estimated_annual_yield_usd. Solo lectura — no "
    "necesita aprobacion.",
    {"type": "object", "properties": {}, "additionalProperties": False},
)
async def list_positions(args: dict[str, Any]) -> dict[str, Any]:
    del args
    cid = await _resolve_eth_connection_id()
    if not cid:
        return _NO_WALLET_RESPONSE
    return await _request("GET", f"/api/v1/connections/{cid}/defi/positions")


@tool(
    "supply",
    "Deposita un asset en el pool de Aave V3 para empezar a generar yield. ESTA "
    "ES UNA OPERACION QUE MUEVE DINERO — al llamar la tool el backend pide la "
    "confirmacion del usuario por su cuenta. No preguntes confirmacion en texto "
    "antes de llamar a la tool.",
    {
        "type": "object",
        "properties": {
            "market_id": {
                "type": "string",
                "description": "ID del mercado, e.g. aave-v3-base-USDC.",
            },
            "asset": {
                "type": "string",
                "description": "Simbolo del asset, e.g. USDC.",
            },
            "amount": {
                "type": "string",
                "description": "Monto a depositar como decimal string, e.g. '100' para 100 USDC.",
            },
        },
        "required": ["market_id", "asset", "amount"],
        "additionalProperties": False,
    },
)
async def supply(args: dict[str, Any]) -> dict[str, Any]:
    cid = await _resolve_eth_connection_id()
    if not cid:
        return _NO_WALLET_RESPONSE
    body = {
        "protocol": "aave",
        "market_id": str(args["market_id"]),
        "asset": str(args["asset"]),
        "amount": str(args["amount"]),
    }
    return await _request("POST", f"/api/v1/connections/{cid}/defi/supply", json_body=body)


@tool(
    "withdraw",
    "Retira un asset previamente depositado en Aave V3. ESTA ES UNA OPERACION "
    "QUE MUEVE DINERO — al llamar la tool el backend pide la confirmacion del "
    "usuario por su cuenta. No preguntes confirmacion en texto antes de llamar "
    "a la tool. amount puede ser un decimal string ('50') o 'max' para retirar "
    "todo lo depositado.",
    {
        "type": "object",
        "properties": {
            "market_id": {
                "type": "string",
                "description": "ID del mercado, e.g. aave-v3-base-USDC.",
            },
            "asset": {
                "type": "string",
                "description": "Simbolo del asset, e.g. USDC.",
            },
            "amount": {
                "type": "string",
                "description": "Monto a retirar como decimal string o 'max' para retirar todo.",
            },
        },
        "required": ["market_id", "asset", "amount"],
        "additionalProperties": False,
    },
)
async def withdraw(args: dict[str, Any]) -> dict[str, Any]:
    cid = await _resolve_eth_connection_id()
    if not cid:
        return _NO_WALLET_RESPONSE
    body = {
        "protocol": "aave",
        "market_id": str(args["market_id"]),
        "asset": str(args["asset"]),
        "amount": str(args["amount"]),
    }
    return await _request("POST", f"/api/v1/connections/{cid}/defi/withdraw", json_body=body)
