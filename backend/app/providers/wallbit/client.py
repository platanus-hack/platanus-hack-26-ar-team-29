"""Wallbit REST client.

Base URL + auth header per https://developer.wallbit.io/docs/quickstart.
All endpoints sit under `/api/public/v1/...` (per quickstart).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx
import structlog

log = structlog.get_logger(__name__)


class WallbitAPIError(Exception):
    def __init__(self, status: int, body: Any, *, endpoint: str | None = None) -> None:
        super().__init__(f"Wallbit API error {status} on {endpoint}: {body}")
        self.status = status
        self.body = body
        self.endpoint = endpoint


class WallbitClient:
    """Thin async client against the Wallbit public API."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> WallbitClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        full_path = f"/api/public/v1{path}"
        try:
            resp = await self._client.request(method, full_path, params=params, json=json)
        except httpx.HTTPError as exc:
            log.warning(
                "wallbit_request_transport_error",
                method=method,
                path=full_path,
                error=str(exc),
            )
            raise WallbitAPIError(0, str(exc), endpoint=full_path) from exc
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            log.warning(
                "wallbit_api_error",
                method=method,
                path=full_path,
                status=resp.status_code,
                body=body,
            )
            raise WallbitAPIError(resp.status_code, body, endpoint=full_path)
        try:
            data = resp.json()
        except Exception:
            data = resp.text
        log.info(
            "wallbit_response",
            method=method,
            path=full_path,
            status=resp.status_code,
        )
        return data

    async def get_checking_balance(self) -> Any:
        return await self._request("GET", "/balance/checking")

    async def get_stocks_balance(self) -> Any:
        return await self._request("GET", "/balance/stocks")

    async def list_transactions(self, limit: int | None = 50) -> Any:
        params = {"limit": limit} if limit is not None else None
        return await self._request("GET", "/transactions", params=params)

    async def get_asset(self, symbol: str) -> Any:
        return await self._request("GET", f"/assets/{symbol}")

    async def place_trade(
        self,
        symbol: str,
        side: str,
        amount_usd: float | None = None,
        shares: float | None = None,
        idempotency_key: str | UUID | None = None,
    ) -> Any:
        payload: dict[str, Any] = {
            "symbol": symbol,
            "direction": side.upper(),
            "order_type": "MARKET",
            "currency": "USD",
        }
        if amount_usd is not None:
            payload["amount"] = amount_usd
        if shares is not None:
            payload["shares"] = shares
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = str(idempotency_key)
        full_path = "/api/public/v1/trades"
        try:
            resp = await self._client.post(full_path, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            log.warning(
                "wallbit_request_transport_error",
                path=full_path,
                error=str(exc),
            )
            raise WallbitAPIError(0, str(exc), endpoint=full_path) from exc
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            log.warning(
                "wallbit_api_error",
                path=full_path,
                status=resp.status_code,
                body=body,
            )
            raise WallbitAPIError(resp.status_code, body, endpoint=full_path)
        try:
            data = resp.json()
        except Exception:
            data = resp.text
        log.info("wallbit_trade_placed", path=full_path, status=resp.status_code)
        return data
