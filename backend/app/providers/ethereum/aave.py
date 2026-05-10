"""Aave V3 Pool registry + ABI fragments + rate conversion helpers.

Phase 2 (per 02-3 §5.13.3). v1 ships Base mainnet only — extending to other
networks is a matter of adding `_AAVE_V3_MARKETS` rows. APY conversion follows
the Aave V3 convention: stored rates are APR in RAY (1e27) units; APY uses
per-second compounding over 365 days.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

# RAY = 1e27 (Aave fixed-point unit for rates and indices).
RAY = Decimal(10) ** 27

# Aave V3 uses 365-day years for rate math.
SECONDS_PER_YEAR = 31_536_000


@dataclass(frozen=True, slots=True)
class AaveMarket:
    """Per-(network, asset) Aave V3 market metadata.

    `pool` is the V3 Pool contract; `a_token` is the rebasing supply receipt
    used by `list_positions` to read the current supplied amount in 1:1 units
    of the underlying.
    """

    network: str
    asset_symbol: str
    asset_address: str
    pool: str
    a_token: str
    decimals: int


# Markets we support today. Keyed by (network, asset_symbol). Adding a row +
# wiring the underlying ERC-20 in `networks.py` is sufficient to extend.
_AAVE_V3_MARKETS: dict[tuple[str, str], AaveMarket] = {
    ("base", "USDC"): AaveMarket(
        network="base",
        asset_symbol="USDC",
        asset_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        pool="0xA238Dd80C259a72e81d7e4664a9801593F98d1c5",
        a_token="0x4e65fE4DbA92790696d040ac24Aa414708F5c0AB",
        decimals=6,
    ),
    ("sepolia", "USDC"): AaveMarket(
        network="sepolia",
        asset_symbol="USDC",
        asset_address="0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8",
        pool="0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951",
        a_token="0x16dA4541aD1807f4443d92D26044C1147406EB80",
        decimals=6,
    ),
}


def get_market(network: str, asset_symbol: str) -> AaveMarket | None:
    return _AAVE_V3_MARKETS.get((network, asset_symbol.upper()))


def list_markets(network: str | None = None, asset_symbol: str | None = None) -> list[AaveMarket]:
    out: list[AaveMarket] = []
    for m in _AAVE_V3_MARKETS.values():
        if network and m.network != network:
            continue
        if asset_symbol and m.asset_symbol != asset_symbol.upper():
            continue
        out.append(m)
    return out


def market_id(m: AaveMarket) -> str:
    """`aave-v3-{network}-{symbol}` per 02-3 §5.13.3."""
    return f"aave-v3-{m.network}-{m.asset_symbol}"


def parse_market_id(mid: str) -> tuple[str, str] | None:
    """Inverse of `market_id`. Returns `(network, asset_symbol)` or None."""
    parts = mid.split("-")
    # `aave`, `v3`, network, symbol — but network slugs may themselves contain
    # dashes (`base-sepolia`). Symbol is always the last segment, so split off
    # the head and rejoin the middle as the network.
    if len(parts) < 4 or parts[0] != "aave" or parts[1] != "v3":
        return None
    network = "-".join(parts[2:-1])
    symbol = parts[-1].upper()
    return network, symbol


# -------- Rate math --------


def ray_apr_to_apy(rate_ray: int) -> float:
    """Convert an Aave RAY-encoded APR to a decimal APY (per-second compounding).

    `rate_ray` is the raw `currentLiquidityRate` / `currentVariableBorrowRate`
    value returned by the Pool. Result is a plain float in the range [0, 1+);
    `0.0432` means 4.32% APY.
    """
    if rate_ray <= 0:
        return 0.0
    apr = Decimal(int(rate_ray)) / RAY  # nominal annual rate (e.g. 0.04 = 4%)
    rate_per_sec = apr / Decimal(SECONDS_PER_YEAR)
    # (1 + r)^n - 1 with n = SECONDS_PER_YEAR. For typical APRs (< 100%) the
    # value of (1 + rate_per_sec) is extremely close to 1, so use ln/exp via
    # Decimal exponentiation through float for the final compounding step —
    # the precision loss here is well below display precision.
    one_plus = float(Decimal(1) + rate_per_sec)
    return one_plus**SECONDS_PER_YEAR - 1.0


def utilization(total_supply_raw: int, total_debt_raw: int) -> float:
    if total_supply_raw <= 0:
        return 0.0
    return float(Decimal(int(total_debt_raw)) / Decimal(int(total_supply_raw)))


# -------- ABI fragments --------

# Aave V3 Pool — minimum to supply / withdraw / read reserve data.
# Source: aave-v3-core IPool.sol.
AAVE_V3_POOL_ABI: list[dict[str, Any]] = [
    {
        "name": "supply",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "onBehalfOf", "type": "address"},
            {"name": "referralCode", "type": "uint16"},
        ],
        "outputs": [],
    },
    {
        "name": "withdraw",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "to", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "getReserveData",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "asset", "type": "address"}],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "components": [
                    {
                        "name": "configuration",
                        "type": "tuple",
                        "components": [{"name": "data", "type": "uint256"}],
                    },
                    {"name": "liquidityIndex", "type": "uint128"},
                    {"name": "currentLiquidityRate", "type": "uint128"},
                    {"name": "variableBorrowIndex", "type": "uint128"},
                    {"name": "currentVariableBorrowRate", "type": "uint128"},
                    {"name": "currentStableBorrowRate", "type": "uint128"},
                    {"name": "lastUpdateTimestamp", "type": "uint40"},
                    {"name": "id", "type": "uint16"},
                    {"name": "aTokenAddress", "type": "address"},
                    {"name": "stableDebtTokenAddress", "type": "address"},
                    {"name": "variableDebtTokenAddress", "type": "address"},
                    {"name": "interestRateStrategyAddress", "type": "address"},
                    {"name": "accruedToTreasury", "type": "uint128"},
                    {"name": "unbacked", "type": "uint128"},
                    {"name": "isolationModeTotalDebt", "type": "uint128"},
                ],
            }
        ],
    },
]

# ERC-20 fragments needed for DeFi flows but not in the read-only abi.py.
ERC20_APPROVE_ABI: list[dict[str, Any]] = [
    {
        "name": "approve",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "allowance",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "totalSupply",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
    },
]
