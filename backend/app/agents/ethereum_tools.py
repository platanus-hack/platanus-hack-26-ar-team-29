from __future__ import annotations

import os
import json
from typing import Any

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool

port = os.getenv("PORT", "8000")
BACKEND_BASE = f"http://127.0.0.1:{port}"


def ethereum_mcp_server():
    return create_sdk_mcp_server(
        name="ethereum",
        version="0.1.0",
        tools=[
            create_ethereum_wallet,
            import_ethereum_wallet,
            send_onchain,
        ],
    )


@tool(
    "create_ethereum_wallet",
    "Crea una nueva billetera custodial de Ethereum. Pidele siempre al usuario en que red quiere crearla antes de llamar la tool.",
    {
        "type": "object",
        "properties": {
            "network": {
                "type": "string",
                "enum": [
                    "sepolia",
                    "holesky",
                    "polygon-amoy",
                    "arbitrum-sepolia",
                    "base-sepolia",
                    "base",
                ],
                "description": "La red en la que crear la billetera.",
            }
        },
        "required": ["network"],
        "additionalProperties": False,
    },
)
async def create_ethereum_wallet(args: dict[str, Any]) -> dict[str, Any]:
    network = args.get("network", "sepolia")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            "POST",
            f"{BACKEND_BASE}/api/v1/connections/ethereum-custodial/create",
            json={"network": network, "label": "Wallet Ethereum", "primary_asset_hint": "ETH"},
            # Note: Since the backend requires user auth, in a real scenario we'd pass headers here.
            # But the agent server might run on the same instance without auth if it's the dev user.
            # The deps.py uses DEV_USER_ID always so it should work.
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
                    "text": f"Ethereum API error {response.status_code}: {payload}",
                }
            ],
            "is_error": True,
        }

    return {"content": [{"type": "text", "text": json.dumps(payload)}], "data": payload}


@tool(
    "import_ethereum_wallet",
    "Inicia sesion / importa una billetera custodial de Ethereum existente mediante una clave privada o frase semilla. Pidele siempre al usuario la clave privada o frase semilla y la red antes de llamar a la tool.",
    {
        "type": "object",
        "properties": {
            "network": {
                "type": "string",
                "enum": [
                    "sepolia",
                    "holesky",
                    "polygon-amoy",
                    "arbitrum-sepolia",
                    "base-sepolia",
                    "base",
                ],
                "description": "La red en la que importar la billetera.",
            },
            "private_key": {
                "type": "string",
                "description": "La clave privada (hex) o frase semilla (mnemonic) de la billetera a importar.",
            },
        },
        "required": ["network", "private_key"],
        "additionalProperties": False,
    },
)
async def import_ethereum_wallet(args: dict[str, Any]) -> dict[str, Any]:
    network = args.get("network", "sepolia")
    private_key = args.get("private_key")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            "POST",
            f"{BACKEND_BASE}/api/v1/connections/ethereum-custodial/import",
            json={
                "network": network,
                "private_key": private_key,
                "label": "Wallet Ethereum",
                "primary_asset_hint": "ETH",
            },
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
                    "text": f"Ethereum API error {response.status_code}: {payload}",
                }
            ],
            "is_error": True,
        }

    return {"content": [{"type": "text", "text": json.dumps(payload)}], "data": payload}


async def _resolve_eth_connection_id() -> str | None:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            "GET",
            f"{BACKEND_BASE}/api/v1/connections",
        )
    try:
        conns = response.json()
    except ValueError:
        return None

    if isinstance(conns, list):
        for c in conns:
            if c.get("connection_type") == "ethereum_custodial" and c.get("status") == "healthy":
                return str(c["id"])
    return None


@tool(
    "send_onchain",
    "Realiza una transferencia de criptomonedas (ETH o un token ERC20 como USDC) hacia otra direccion en la red. ESTA ES UNA OPERACION QUE MUEVE DINERO — al llamar la tool el backend pide confirmacion del usuario. Llama directamente a la tool. No necesitas pedir conexion.",
    {
        "type": "object",
        "properties": {
            "asset": {
                "type": "string",
                "description": "El ticker o simbolo de la cripto (e.g. 'ETH', 'USDC')",
            },
            "to": {
                "type": "string",
                "description": "La direccion hexadecimal de destino ('0x...')",
            },
            "amount": {
                "type": "string",
                "description": "El monto a enviar (en formato texto con decimales, e.g. '0.5' o '150.25')",
            },
            "gas_speed": {
                "type": "string",
                "enum": ["slow", "standard", "fast"],
                "description": "Opcional: velocidad/comision del gas a pagar. Por defecto 'standard'.",
            },
        },
        "required": ["asset", "to", "amount"],
        "additionalProperties": False,
    },
)
async def send_onchain(args: dict[str, Any]) -> dict[str, Any]:
    connection_id = await _resolve_eth_connection_id()
    if not connection_id:
        return {
            "content": [
                {"type": "text", "text": "No se encontro ninguna billetera Ethereum conectada."}
            ],
            "is_error": True,
        }

    asset = args.get("asset")
    to = args.get("to")
    amount = args.get("amount")
    gas_speed = args.get("gas_speed", "standard")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            "POST",
            f"{BACKEND_BASE}/api/v1/connections/{connection_id}/onchain/transfer",
            json={
                "asset": asset,
                "to": to,
                "amount": amount,
                "gas_speed": gas_speed,
            },
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
                    "text": f"Error realizando transferencia:\nStatus: {response.status_code}\nDetalles:\n{json.dumps(payload, indent=2)}",
                }
            ],
            "is_error": True,
        }

    return {
        "content": [
            {
                "type": "text",
                "text": f"Transferencia enviada satisfactoriamente:\n{json.dumps(payload, indent=2)}",
            }
        ],
        "data": payload,
    }
