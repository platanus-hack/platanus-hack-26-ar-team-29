from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

TOOL_LABELS = {
    # Wallbit
    "get_checking_balance": "Consultar Saldo",
    "get_stocks_balance": "Consultar Inversiones",
    "list_transactions": "Listar Transacciones",
    "get_asset": "Consultar Activo",
    "create_trade": "Crear Orden de Trade",
    "show_table": "Mostrar Tabla",
    "get_all_balances": "Consultar Balances Totales",
    "mcp__wallbit__get_checking_balance": "Consultar Saldo",
    "mcp__wallbit__get_stocks_balance": "Consultar Inversiones",
    "mcp__wallbit__list_transactions": "Listar Transacciones",
    "mcp__wallbit__get_asset": "Consultar Activo",
    "mcp__wallbit__create_trade": "Crear Orden de Trade",
    "mcp__wallbit__show_table": "Mostrar Tabla",
    "mcp__wallbit__get_all_balances": "Consultar Balances Totales",

    # UI / Internos
    "AskUserQuestion": "Hacer Pregunta",
    "request_credential": "Solicitar Credencial",
    "mcp__ui__request_credential": "Solicitar Credencial",

    # Ethereum
    "send_onchain": "Transferir Criptomonedas",
    "mcp__ethereum__send_onchain": "Transferir Criptomonedas",
    "create_ethereum_wallet": "Crear Billetera",
    "mcp__ethereum__create_ethereum_wallet": "Crear Billetera",
    "import_ethereum_wallet": "Importar Billetera",
    "mcp__ethereum__import_ethereum_wallet": "Importar Billetera",

    # DeFi
    "list_markets": "Listar Mercados DeFi",
    "mcp__defi__list_markets": "Listar Mercados DeFi",
    "get_market": "Consultar Mercado DeFi",
    "mcp__defi__get_market": "Consultar Mercado DeFi",
    "list_positions": "Listar Posiciones DeFi",
    "mcp__defi__list_positions": "Listar Posiciones DeFi",
    "supply": "Depositar en DeFi",
    "mcp__defi__supply": "Depositar en DeFi",
    "withdraw": "Retirar de DeFi",
    "mcp__defi__withdraw": "Retirar de DeFi",
}


def format_tool_name(tool_name: str | None) -> str:
    """Returns the human-readable name of the tool, or attempts to format it if not found."""
    if not tool_name:
        return "Unknown Tool"

    if tool_name in TOOL_LABELS:
        return TOOL_LABELS[tool_name]

    # Fallback: remove mcp__ prefixes and format snake_case to Title Case
    clean_name = tool_name.replace("mcp__wallbit__", "").replace("mcp__", "")
    return clean_name.replace("_", " ").title()


@dataclass(frozen=True)
class ChatAction:
    id: str
    label: str

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "label": self.label}


@dataclass(frozen=True)
class AgentEvent:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, **self.payload}


def summarize_value(value: Any, *, max_chars: int = 600) -> str:
    try:
        rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        rendered = repr(value)

    if len(rendered) <= max_chars:
        return rendered
    return f"{rendered[: max_chars - 3]}..."


def approval_requested_event(
    *,
    approval_id: str,
    tool_name: str,
    input_data: dict[str, Any],
) -> AgentEvent:
    return AgentEvent(
        "approval_requested",
        {
            "approval_id": approval_id,
            "tool_name": tool_name,
            "title": "Confirmar operacion",
            "message": "Atajo quiere ejecutar esta operacion en Wallbit.",
            "input": input_data,
            "actions": [
                ChatAction("confirm", "Confirm").to_dict(),
                ChatAction("reject", "Reject").to_dict(),
            ],
        },
    )


def input_requested_event(
    *,
    input_id: str,
    title: str,
    question: str,
    options: list[dict[str, str]],
    multi_select: bool,
) -> AgentEvent:
    return AgentEvent(
        "input_requested",
        {
            "input_id": input_id,
            "title": title,
            "question": question,
            "options": options,
            "multi_select": multi_select,
        },
    )


def input_resolved_event(
    *,
    input_id: str,
    selected_options: list[str],
) -> AgentEvent:
    return AgentEvent(
        "input_resolved",
        {
            "input_id": input_id,
            "selected_options": selected_options,
        },
    )


def approval_resolved_event(
    *,
    approval_id: str,
    tool_name: str,
    decision: str,
) -> AgentEvent:
    return AgentEvent(
        "approval_resolved",
        {
            "approval_id": approval_id,
            "tool_name": tool_name,
            "decision": decision,
        },
    )


def credential_requested_event(
    *,
    request_id: str,
    title: str,
    instructions: str,
    kind: str,
    placeholder: str | None = None,
) -> AgentEvent:
    return AgentEvent(
        "credential_requested",
        {
            "request_id": request_id,
            "title": title,
            "instructions": instructions,
            "kind": kind,
            "placeholder": placeholder,
        },
    )


def credential_resolved_event(
    *,
    request_id: str,
    cancelled: bool = False,
) -> AgentEvent:
    return AgentEvent(
        "credential_resolved",
        {"request_id": request_id, "cancelled": cancelled},
    )


def error_event(message: str, *, details: Any | None = None) -> AgentEvent:
    payload: dict[str, Any] = {"message": message}
    if details is not None:
        payload["details"] = details
    return AgentEvent("error", payload)
