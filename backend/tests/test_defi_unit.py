"""Pure-unit tests for the Aave V3 DeFi adapter helpers.

No DB, no RPC. Exercises the parts of `app/providers/ethereum/aave.py` and
`app/services/defi.py` that don't need a chain.
"""

from __future__ import annotations

import pytest

from app.providers.ethereum import aave


def test_market_id_round_trip() -> None:
    m = aave.get_market("base", "USDC")
    assert m is not None
    mid = aave.market_id(m)
    assert mid == "aave-v3-base-USDC"
    parsed = aave.parse_market_id(mid)
    assert parsed == ("base", "USDC")


def test_market_id_round_trip_with_dashed_network() -> None:
    # Hypothetical: Aave on `base-sepolia`. `parse_market_id` must recover the
    # network even when the slug contains a dash, because the symbol is the
    # last segment. We don't actually ship this market — round-trip only.
    parsed = aave.parse_market_id("aave-v3-base-sepolia-USDC")
    assert parsed == ("base-sepolia", "USDC")


def test_parse_market_id_rejects_garbage() -> None:
    assert aave.parse_market_id("morpho-v3-base-USDC") is None
    assert aave.parse_market_id("aave-v2-base-USDC") is None
    assert aave.parse_market_id("aave-v3-base") is None  # too few segments


def test_list_markets_filters() -> None:
    assert aave.list_markets() == [aave.get_market("base", "USDC")]
    assert aave.list_markets(network="base") == [aave.get_market("base", "USDC")]
    assert aave.list_markets(network="sepolia") == []
    assert aave.list_markets(asset_symbol="usdc") == [aave.get_market("base", "USDC")]
    assert aave.list_markets(asset_symbol="ETH") == []


def test_ray_apr_to_apy_zero() -> None:
    assert aave.ray_apr_to_apy(0) == 0.0
    assert aave.ray_apr_to_apy(-1) == 0.0


@pytest.mark.parametrize(
    "apr_decimal,expected_apy_low,expected_apy_high",
    [
        # 5% APR with continuous-ish compounding ≈ 5.127% APY.
        (0.05, 0.0510, 0.0515),
        # 10% APR ≈ 10.517% APY.
        (0.10, 0.1050, 0.1054),
        # 1% APR ≈ 1.005% APY.
        (0.01, 0.01004, 0.01006),
    ],
)
def test_ray_apr_to_apy_matches_continuous_compounding(
    apr_decimal: float, expected_apy_low: float, expected_apy_high: float
) -> None:
    rate_ray = int(apr_decimal * float(aave.RAY))
    apy = aave.ray_apr_to_apy(rate_ray)
    assert expected_apy_low <= apy <= expected_apy_high, apy


def test_utilization_edge_cases() -> None:
    assert aave.utilization(0, 0) == 0.0
    assert aave.utilization(0, 100) == 0.0  # no supply ⇒ 0, not divide-by-zero
    assert aave.utilization(100, 0) == 0.0
    assert abs(aave.utilization(1000, 750) - 0.75) < 1e-9


def test_supported_pool_address_is_checksummed_aave_v3_base() -> None:
    m = aave.get_market("base", "USDC")
    assert m is not None
    # Sanity: known Aave V3 Pool on Base mainnet (Aave Address Book).
    assert m.pool == "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"
    # Circle native USDC on Base mainnet.
    assert m.asset_address == "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    # aBasUSDC on Base mainnet.
    assert m.a_token == "0x4e65fE4DbA92790696d040ac24Aa414708F5c0AB"
    assert m.decimals == 6


def test_pool_abi_has_required_functions() -> None:
    names = {entry["name"] for entry in aave.AAVE_V3_POOL_ABI}
    assert {"supply", "withdraw", "getReserveData"}.issubset(names)


def test_erc20_approve_abi_has_required_functions() -> None:
    names = {entry["name"] for entry in aave.ERC20_APPROVE_ABI}
    assert {"approve", "allowance", "totalSupply"}.issubset(names)


def test_defi_amount_helpers() -> None:
    from app.services.defi import _decimal_amount_to_raw, _raw_to_decimal_str

    # 100 USDC (6 decimals) → 100_000_000.
    assert _decimal_amount_to_raw("100", 6) == 100_000_000
    assert _decimal_amount_to_raw("0.5", 6) == 500_000
    # Round-trip.
    assert _raw_to_decimal_str(100_000_000, 6) == "100"
    assert _raw_to_decimal_str(500_000, 6) == "0.5"
    assert _raw_to_decimal_str(0, 6) == "0"


def test_decimal_amount_rejects_zero_and_negative() -> None:
    from app.common.errors import APIError
    from app.services.defi import _decimal_amount_to_raw

    with pytest.raises(APIError):
        _decimal_amount_to_raw("0", 6)
    with pytest.raises(APIError):
        _decimal_amount_to_raw("-1", 6)
    with pytest.raises(APIError):
        _decimal_amount_to_raw("not a number", 6)
