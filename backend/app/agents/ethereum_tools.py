from __future__ import annotations

from typing import Any

import json
import httpx
from claude_agent_sdk import create_sdk_mcp_server, tool


def ethereum_mcp_server():
    return create_sdk_mcp_server(
        name="ethereum",
        version="0.1.0",
        tools=[
            create_ethereum_wallet,
        ],
    )


@tool(
    "create_ethereum_wallet",
    "Crea una nueva billetera custodial de Ethereum (sepolia). Devolvera la direccion y la frase semilla.",
    {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
)
async def create_ethereum_wallet(args: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            "POST",
            "http://127.0.0.1:8000/api/v1/connections/ethereum-custodial/create",
            json={"network": "sepolia", "label": "Wallet Ethereum", "primary_asset_hint": "ETH"},
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
