from __future__ import annotations

import json
from typing import Any

import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool


def ethereum_mcp_server():
    return create_sdk_mcp_server(
        name="ethereum",
        version="0.1.0",
        tools=[
            create_ethereum_wallet,
            import_ethereum_wallet,
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
            "http://127.0.0.1:8000/api/v1/connections/ethereum-custodial/create",
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
            "http://127.0.0.1:8000/api/v1/connections/ethereum-custodial/import",
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
