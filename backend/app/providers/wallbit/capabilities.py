"""WallbitProvider — implements Provider ABC for Wallbit."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx

from app.providers.base import Provider
from app.providers.wallbit.auth import WallbitCredentials
from app.providers.wallbit.client import WallbitClient


class WallbitProvider(Provider):
    name = "wallbit"

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        # A shared httpx.AsyncClient lets us pool connections across calls
        # but we still build a per-request WallbitClient (they're cheap).
        self._http = httpx.AsyncClient(timeout=10.0)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def healthcheck(self) -> bool:
        return True

    def client(self, creds: WallbitCredentials) -> WallbitClient:
        # Each WallbitClient owns its own httpx.AsyncClient with auth headers.
        return WallbitClient(api_key=creds.api_key, base_url=self.base_url)

    async def read_balance(self, creds: WallbitCredentials) -> dict[str, Any]:
        async with self.client(creds) as wc:
            checking = await wc.get_checking_balance()
            try:
                stocks = await wc.get_stocks_balance()
            except Exception:
                stocks = []
            return {"checking": checking, "stocks": stocks}

    async def read_transactions(self, creds: WallbitCredentials, limit: int = 50) -> Any:
        async with self.client(creds) as wc:
            return await wc.list_transactions(limit=limit)

    async def place_trade(
        self,
        creds: WallbitCredentials,
        args: dict[str, Any],
        idempotency_key: UUID | str,
    ) -> Any:
        symbol = str(args["symbol"]).upper()
        side = str(args.get("side", "buy")).lower()
        amount_usd = args.get("amount_usd") or args.get("usd")
        shares = args.get("shares")
        async with self.client(creds) as wc:
            return await wc.place_trade(
                symbol=symbol,
                side=side,
                amount_usd=float(amount_usd) if amount_usd is not None else None,
                shares=float(shares) if shares is not None else None,
                idempotency_key=str(idempotency_key),
            )
