"""Agent runtime exports + tool bootstrap."""

from __future__ import annotations

from typing import Any

from app.agents.tool_dispatcher import ToolContext, ToolDef, ToolDispatcher
from app.services.portfolio import PortfolioService


async def _read_balances_handler(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
    async with ctx.sessionmaker() as db:
        svc = PortfolioService(session=db, wallbit_base_url=ctx.wallbit_base_url)
        rows = await svc.read_balances(user_id=ctx.user_id)
    return {"rows": rows, "count": len(rows)}


async def _read_transactions_handler(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
    limit = int(args.get("limit", 20)) if args else 20
    async with ctx.sessionmaker() as db:
        svc = PortfolioService(session=db, wallbit_base_url=ctx.wallbit_base_url)
        rows = await svc.read_transactions(user_id=ctx.user_id, limit=limit)
    return {"rows": rows, "count": len(rows)}


def bootstrap_tools(dispatcher: ToolDispatcher) -> None:
    dispatcher.register(
        ToolDef(
            name="read_balances",
            description=(
                "Read the current balances from the user's Wallbit account "
                "(USD cash plus stock/ETF positions). Returns a list of rows."
            ),
            input_schema={"type": "object", "properties": {}, "required": []},
            category="read",
            handler=_read_balances_handler,
        )
    )
    dispatcher.register(
        ToolDef(
            name="read_transactions",
            description=(
                "Read the most recent Wallbit transactions for the user. "
                "Optional integer 'limit' (default 20)."
            ),
            input_schema={
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
                "required": [],
            },
            category="read",
            handler=_read_transactions_handler,
        )
    )
    dispatcher.register(
        ToolDef(
            name="propose_trade",
            description=(
                "Propose (DO NOT EXECUTE) a buy or sell of a stock/ETF on Wallbit. "
                "The proposal will be shown to the user for one-shot approval. "
                "Provide symbol (e.g. AAPL), side ('buy' or 'sell'), and exactly "
                "one of amount_usd or shares."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Ticker, e.g. AAPL"},
                    "side": {"type": "string", "enum": ["buy", "sell"]},
                    "amount_usd": {
                        "type": "number",
                        "description": "USD notional for the order.",
                    },
                    "shares": {
                        "type": "number",
                        "description": "Share count for the order.",
                    },
                    "rationale_es": {
                        "type": "string",
                        "description": "Short Spanish explanation shown to the user.",
                    },
                },
                "required": ["symbol", "side"],
            },
            category="write",
            handler=None,
        )
    )


__all__ = ["ToolContext", "ToolDef", "ToolDispatcher", "bootstrap_tools"]
