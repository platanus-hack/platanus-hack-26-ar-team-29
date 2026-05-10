from __future__ import annotations

from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool


def ui_mcp_server():
    return create_sdk_mcp_server(
        name="ui",
        version="0.1.0",
        tools=[request_credential],
    )


@tool(
    "request_credential",
    "Solicita al usuario un dato sensible (frase semilla, clave privada, "
    "API key) a traves de un componente seguro en la UI. La UI le pide al "
    "usuario que pegue el dato y devuelve el valor entrado al agente. "
    "Usala SIEMPRE en lugar de pedir el dato en texto en el chat — pedirlo "
    "en texto deja la frase semilla / clave privada en el historial visible "
    "del chat, lo cual es un riesgo de seguridad. Despues de obtener el "
    "valor, podes pasarlo a otra tool (e.g. mcp__ethereum__import_ethereum_wallet).",
    {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": (
                    "Titulo corto del campo, e.g. 'Frase semilla' o 'Clave privada'."
                ),
            },
            "kind": {
                "type": "string",
                "enum": ["seed_phrase", "private_key", "api_key", "secret"],
                "description": (
                    "Tipo de dato — 'seed_phrase' para BIP-39 (textarea, mascara), "
                    "'private_key' para hex (input, mascara), 'api_key' / 'secret' para otros."
                ),
            },
            "instructions": {
                "type": "string",
                "description": (
                    "Texto explicativo para el usuario, una o dos frases en castellano."
                ),
            },
            "placeholder": {
                "type": "string",
                "description": (
                    "Placeholder opcional del input, e.g. '12 o 24 palabras separadas por espacios'."
                ),
            },
        },
        "required": ["title", "kind", "instructions"],
        "additionalProperties": False,
    },
)
async def request_credential(args: dict[str, Any]) -> dict[str, Any]:
    """Echo the user-entered value back to the agent.

    The bridge intercepts this tool call in `can_use_tool`, prompts the user
    via `credential_requested`, awaits their input, and sets
    `updated_input = {"value": <entered text>, "kind": ...}`. The SDK then
    invokes this function with that input. We simply return the value as the
    tool result so the agent can use it in subsequent tool calls.
    """
    value = args.get("value", "")
    kind = args.get("kind", "secret")
    if not isinstance(value, str) or not value:
        return {
            "content": [
                {"type": "text", "text": "El usuario no proporciono el dato."}
            ],
            "is_error": True,
        }
    # Surface the value as the tool result. Marked sensitive in the text
    # output so logging/redaction layers can hide it; the agent sees the raw
    # value in its tool-result context.
    return {
        "content": [
            {
                "type": "text",
                "text": f"<credential kind={kind}>{value}</credential>",
            }
        ],
        "data": {"value": value, "kind": kind},
    }
