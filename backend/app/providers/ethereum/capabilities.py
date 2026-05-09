"""EthereumCustodialProvider — implements Provider ABC.

Phase 1: ``read_balance``, ``read_transactions``, ``send_onchain``.
Phase 2 (now shipped, Aave V3 only): ``supply_defi``, ``withdraw_defi``,
``list_defi_markets``, ``get_defi_market``, ``list_defi_positions``.
"""

from __future__ import annotations

from app.providers.base import Provider
from app.providers.ethereum.client import EthereumClient

PHASE_1_CAPABILITIES: list[str] = [
    "read_balance",
    "read_transactions",
    "send_onchain",
    "supply_defi",
    "withdraw_defi",
    "list_defi_markets",
    "get_defi_market",
    "list_defi_positions",
]


class EthereumCustodialProvider(Provider):
    name = "ethereum_custodial"

    def __init__(self, rpc_urls: dict[str, str]) -> None:
        self._client = EthereumClient(rpc_urls=rpc_urls)

    @property
    def client(self) -> EthereumClient:
        return self._client

    async def healthcheck(self) -> bool:
        # Cheap chainId call against Sepolia (the canonical default).
        try:
            await self._client.chain_id("sepolia")
        except Exception:
            return False
        return True
