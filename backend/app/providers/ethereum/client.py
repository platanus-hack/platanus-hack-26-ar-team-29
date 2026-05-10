"""Thin synchronous wrapper around web3.py, exposed as async via to_thread.

One ``Web3`` instance per network, cached. Methods cover the surface needed by
Phase 1: balances, gas suggestions, ETH + ERC-20 transfers, simulation, receipts.

The class never persists or accepts a private key beyond the call boundary —
callers decrypt at the service layer and pass the hex key in.
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any

import structlog
from eth_account import Account
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.exceptions import ContractLogicError, Web3Exception

from app.providers.ethereum.aave import AAVE_V3_POOL_ABI, ERC20_APPROVE_ABI
from app.providers.ethereum.abi import ERC20_ABI

log = structlog.get_logger(__name__)


class EthereumClientError(Exception):
    """Raised for normalized RPC / web3 failures.

    ``raw`` is included for logs but is intentionally NOT surfaced to API responses
    (callers must redact). ``user_message_es`` is a Spanish-first summary safe to surface.
    """

    def __init__(self, user_message_es: str, raw: str | None = None) -> None:
        super().__init__(user_message_es)
        self.user_message_es = user_message_es
        self.raw = raw


class EthereumClient:
    """Per-network web3 client.

    Cached ``Web3`` instances live in ``_w3`` keyed by network slug.
    """

    def __init__(self, rpc_urls: dict[str, str]) -> None:
        self._rpc_urls = rpc_urls
        self._w3: dict[str, Web3] = {}

    def _web3(self, network: str) -> Web3:
        cached = self._w3.get(network)
        if cached is not None:
            return cached
        url = self._rpc_urls.get(network)
        if not url:
            raise EthereumClientError(
                user_message_es="No hay un RPC configurado para esta red.",
                raw=f"missing_rpc_url:{network}",
            )
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 15}))
        self._w3[network] = w3
        return w3

    # ---------- helpers ----------

    @staticmethod
    def derive_address(private_key: str) -> ChecksumAddress:
        return Account.from_key(private_key).address  # type: ignore[no-any-return]

    @staticmethod
    def to_checksum(addr: str) -> ChecksumAddress:
        return Web3.to_checksum_address(addr)

    @staticmethod
    def is_address(addr: str) -> bool:
        try:
            return Web3.is_address(addr)
        except Exception:
            return False

    # ---------- chain reads ----------

    async def chain_id(self, network: str) -> int:
        def _call() -> int:
            return int(self._web3(network).eth.chain_id)

        return await asyncio.to_thread(_call)

    async def get_eth_balance(self, network: str, address: str) -> int:
        def _call() -> int:
            w3 = self._web3(network)
            return int(w3.eth.get_balance(Web3.to_checksum_address(address)))

        return await asyncio.to_thread(_call)

    async def get_erc20_balance(
        self, network: str, address: str, token_contract: str
    ) -> tuple[int, int]:
        """Return ``(balance_raw, decimals)``."""

        def _call() -> tuple[int, int]:
            w3 = self._web3(network)
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(token_contract), abi=ERC20_ABI
            )
            bal = int(contract.functions.balanceOf(Web3.to_checksum_address(address)).call())
            dec = int(contract.functions.decimals().call())
            return bal, dec

        return await asyncio.to_thread(_call)

    async def get_gas_price_wei(self, network: str) -> int:
        def _call() -> int:
            w3 = self._web3(network)
            return int(w3.eth.gas_price)

        return await asyncio.to_thread(_call)

    async def estimate_gas(self, network: str, tx: dict[str, Any]) -> int:
        def _call() -> int:
            w3 = self._web3(network)
            try:
                return int(w3.eth.estimate_gas(tx))  # type: ignore[arg-type]
            except ContractLogicError as exc:
                raise EthereumClientError(
                    user_message_es="La simulación de la transacción revirtió.",
                    raw=str(exc),
                ) from exc
            except Web3Exception as exc:
                raise EthereumClientError(
                    user_message_es="No se pudo estimar el gas.",
                    raw=str(exc),
                ) from exc

        return await asyncio.to_thread(_call)

    async def simulate_call(self, network: str, tx: dict[str, Any]) -> dict[str, Any]:
        """Best-effort dry-run via eth_call + estimate_gas.

        Returns ``{"ok": True, "gas_estimate": int}`` on success, otherwise
        ``{"ok": False, "revert_summary": str}``. Raw revert strings are NOT
        surfaced to API responses; callers redact.
        """

        def _call() -> dict[str, Any]:
            w3 = self._web3(network)
            try:
                w3.eth.call(tx)  # type: ignore[arg-type]
            except ContractLogicError as exc:
                return {"ok": False, "revert_summary": "execution_reverted", "raw": str(exc)}
            except Web3Exception as exc:
                return {"ok": False, "revert_summary": "rpc_error", "raw": str(exc)}
            try:
                gas = int(w3.eth.estimate_gas(tx))  # type: ignore[arg-type]
            except (ContractLogicError, Web3Exception) as exc:
                return {"ok": False, "revert_summary": "estimate_failed", "raw": str(exc)}
            return {"ok": True, "gas_estimate": gas}

        return await asyncio.to_thread(_call)

    # ---------- writes ----------

    async def send_eth(
        self,
        network: str,
        from_priv: str,
        to: str,
        amount_wei: int,
    ) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            w3 = self._web3(network)
            acct = Account.from_key(from_priv)
            to_addr = Web3.to_checksum_address(to)
            chain_id = int(w3.eth.chain_id)
            nonce = int(w3.eth.get_transaction_count(acct.address))
            gas_price = int(w3.eth.gas_price)

            tx: dict[str, Any] = {
                "from": acct.address,
                "to": to_addr,
                "value": int(amount_wei),
                "nonce": nonce,
                "chainId": chain_id,
                "gasPrice": gas_price,
            }
            try:
                tx["gas"] = int(w3.eth.estimate_gas(tx))  # type: ignore[arg-type]
            except (ContractLogicError, Web3Exception) as exc:
                raise EthereumClientError(
                    user_message_es=(
                        "No se pudo enviar: la transacción revertiría "
                        "(saldo insuficiente o cuenta sin gas)."
                    ),
                    raw=str(exc),
                ) from exc

            signed = acct.sign_transaction(tx)
            try:
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            except Web3Exception as exc:
                raise EthereumClientError(
                    user_message_es="El nodo rechazó la transacción.",
                    raw=str(exc),
                ) from exc
            return {
                "tx_hash": tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash),
                "gas": tx["gas"],
                "gas_price_wei": gas_price,
            }

        return await asyncio.to_thread(_call)

    async def send_erc20(
        self,
        network: str,
        from_priv: str,
        token_contract: str,
        to: str,
        amount_raw: int,
    ) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            w3 = self._web3(network)
            acct = Account.from_key(from_priv)
            to_addr = Web3.to_checksum_address(to)
            token_addr = Web3.to_checksum_address(token_contract)
            chain_id = int(w3.eth.chain_id)
            nonce = int(w3.eth.get_transaction_count(acct.address))
            gas_price = int(w3.eth.gas_price)
            contract = w3.eth.contract(address=token_addr, abi=ERC20_ABI)

            try:
                tx = contract.functions.transfer(to_addr, int(amount_raw)).build_transaction(
                    {  # type: ignore[arg-type]
                        "from": acct.address,
                        "nonce": nonce,
                        "chainId": chain_id,
                        "gasPrice": gas_price,
                    }
                )
            except (ContractLogicError, Web3Exception) as exc:
                raise EthereumClientError(
                    user_message_es=(
                        "No se pudo construir la transferencia (saldo insuficiente "
                        "o token no compatible)."
                    ),
                    raw=str(exc),
                ) from exc

            signed = acct.sign_transaction(tx)
            try:
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            except Web3Exception as exc:
                raise EthereumClientError(
                    user_message_es="El nodo rechazó la transacción.",
                    raw=str(exc),
                ) from exc
            return {
                "tx_hash": tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash),
                "gas": int(tx.get("gas") or 0),
                "gas_price_wei": gas_price,
            }

        return await asyncio.to_thread(_call)

    # ---------- ERC-20 approve / allowance / totalSupply ----------

    async def erc20_allowance(
        self, network: str, owner: str, token_contract: str, spender: str
    ) -> int:
        def _call() -> int:
            w3 = self._web3(network)
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(token_contract),
                abi=ERC20_APPROVE_ABI,
            )
            return int(
                contract.functions.allowance(
                    Web3.to_checksum_address(owner),
                    Web3.to_checksum_address(spender),
                ).call()
            )

        return await asyncio.to_thread(_call)

    async def erc20_total_supply(self, network: str, token_contract: str) -> int:
        def _call() -> int:
            w3 = self._web3(network)
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(token_contract),
                abi=ERC20_APPROVE_ABI,
            )
            return int(contract.functions.totalSupply().call())

        return await asyncio.to_thread(_call)

    async def erc20_approve(
        self,
        network: str,
        from_priv: str,
        token_contract: str,
        spender: str,
        amount_raw: int,
    ) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            w3 = self._web3(network)
            acct = Account.from_key(from_priv)
            token_addr = Web3.to_checksum_address(token_contract)
            spender_addr = Web3.to_checksum_address(spender)
            chain_id = int(w3.eth.chain_id)
            nonce = int(w3.eth.get_transaction_count(acct.address))
            gas_price = int(w3.eth.gas_price)
            contract = w3.eth.contract(address=token_addr, abi=ERC20_APPROVE_ABI)
            try:
                tx = contract.functions.approve(spender_addr, int(amount_raw)).build_transaction(
                    {  # type: ignore[arg-type]
                        "from": acct.address,
                        "nonce": nonce,
                        "chainId": chain_id,
                        "gasPrice": gas_price,
                    }
                )
            except (ContractLogicError, Web3Exception) as exc:
                raise EthereumClientError(
                    user_message_es="No se pudo construir el approve.",
                    raw=str(exc),
                ) from exc
            signed = acct.sign_transaction(tx)
            try:
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            except Web3Exception as exc:
                raise EthereumClientError(
                    user_message_es="El nodo rechazó el approve.",
                    raw=str(exc),
                ) from exc
            return {
                "tx_hash": tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash),
                "gas": int(tx.get("gas") or 0),
                "gas_price_wei": gas_price,
            }

        return await asyncio.to_thread(_call)

    # ---------- Aave V3 Pool ----------

    async def aave_get_reserve_data(
        self, network: str, pool_address: str, asset_address: str
    ) -> dict[str, Any]:
        """Read `getReserveData(asset)` and return a flat dict.

        Subset of ReserveData useful to the service layer:
        currentLiquidityRate, currentVariableBorrowRate (RAY APR),
        aTokenAddress, variableDebtTokenAddress.
        """

        def _call() -> dict[str, Any]:
            w3 = self._web3(network)
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address), abi=AAVE_V3_POOL_ABI
            )
            data = contract.functions.getReserveData(Web3.to_checksum_address(asset_address)).call()
            # Tuple positions match the struct definition in aave.py.
            return {
                "configuration": int(data[0][0]),
                "liquidity_index": int(data[1]),
                "current_liquidity_rate": int(data[2]),
                "variable_borrow_index": int(data[3]),
                "current_variable_borrow_rate": int(data[4]),
                "current_stable_borrow_rate": int(data[5]),
                "last_update_timestamp": int(data[6]),
                "id": int(data[7]),
                "a_token_address": str(data[8]),
                "stable_debt_token_address": str(data[9]),
                "variable_debt_token_address": str(data[10]),
                "interest_rate_strategy_address": str(data[11]),
                "accrued_to_treasury": int(data[12]),
                "unbacked": int(data[13]),
                "isolation_mode_total_debt": int(data[14]),
            }

        return await asyncio.to_thread(_call)

    async def aave_supply(
        self,
        network: str,
        from_priv: str,
        pool_address: str,
        asset_address: str,
        amount_raw: int,
    ) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            w3 = self._web3(network)
            acct = Account.from_key(from_priv)
            pool = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address), abi=AAVE_V3_POOL_ABI
            )
            chain_id = int(w3.eth.chain_id)
            nonce = int(w3.eth.get_transaction_count(acct.address))
            gas_price = int(w3.eth.gas_price)
            try:
                tx = pool.functions.supply(
                    Web3.to_checksum_address(asset_address),
                    int(amount_raw),
                    acct.address,
                    0,
                ).build_transaction(
                    {  # type: ignore[arg-type]
                        "from": acct.address,
                        "nonce": nonce,
                        "chainId": chain_id,
                        "gasPrice": gas_price,
                    }
                )
            except (ContractLogicError, Web3Exception) as exc:
                raise EthereumClientError(
                    user_message_es=(
                        "No se pudo construir el supply (¿faltó approve o saldo insuficiente?)."
                    ),
                    raw=str(exc),
                ) from exc
            signed = acct.sign_transaction(tx)
            try:
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            except Web3Exception as exc:
                raise EthereumClientError(
                    user_message_es="El nodo rechazó el supply.",
                    raw=str(exc),
                ) from exc
            return {
                "tx_hash": tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash),
                "gas": int(tx.get("gas") or 0),
                "gas_price_wei": gas_price,
            }

        return await asyncio.to_thread(_call)

    async def aave_withdraw(
        self,
        network: str,
        from_priv: str,
        pool_address: str,
        asset_address: str,
        amount_raw: int,
        to: str,
    ) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            w3 = self._web3(network)
            acct = Account.from_key(from_priv)
            pool = w3.eth.contract(
                address=Web3.to_checksum_address(pool_address), abi=AAVE_V3_POOL_ABI
            )
            chain_id = int(w3.eth.chain_id)
            nonce = int(w3.eth.get_transaction_count(acct.address))
            gas_price = int(w3.eth.gas_price)
            try:
                tx = pool.functions.withdraw(
                    Web3.to_checksum_address(asset_address),
                    int(amount_raw),
                    Web3.to_checksum_address(to),
                ).build_transaction(
                    {  # type: ignore[arg-type]
                        "from": acct.address,
                        "nonce": nonce,
                        "chainId": chain_id,
                        "gasPrice": gas_price,
                    }
                )
            except (ContractLogicError, Web3Exception) as exc:
                raise EthereumClientError(
                    user_message_es=(
                        "No se pudo construir el withdraw (¿saldo en Aave insuficiente?)."
                    ),
                    raw=str(exc),
                ) from exc
            signed = acct.sign_transaction(tx)
            try:
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            except Web3Exception as exc:
                raise EthereumClientError(
                    user_message_es="El nodo rechazó el withdraw.",
                    raw=str(exc),
                ) from exc
            return {
                "tx_hash": tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash),
                "gas": int(tx.get("gas") or 0),
                "gas_price_wei": gas_price,
            }

        return await asyncio.to_thread(_call)

    async def get_tx_receipt(self, network: str, tx_hash: str) -> dict[str, Any] | None:
        def _call() -> dict[str, Any] | None:
            w3 = self._web3(network)
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)  # type: ignore[arg-type]
            except Web3Exception:
                return None
            if receipt is None:
                return None
            return dict(receipt)  # type: ignore[arg-type]

        return await asyncio.to_thread(_call)

    # ---------- helpers for service layer ----------

    @staticmethod
    def wei_to_eth_str(wei: int) -> str:
        # Decimal string with up to 18 fractional digits, trimmed.
        d = Decimal(int(wei)) / Decimal(10**18)
        # Use a fixed but trimmed string representation.
        s = format(d, "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s or "0"

    @staticmethod
    def wei_to_gwei_float(wei: int) -> float:
        return float(Decimal(int(wei)) / Decimal(10**9))
