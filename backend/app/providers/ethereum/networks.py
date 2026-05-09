"""Network registry for the custodial Ethereum provider.

Locked decision (02-3 §14 row 28): testnets only in v1. Submitting any mainnet
slug returns 400 NETWORK_NOT_ALLOWED at the service layer.
"""

from __future__ import annotations

from dataclasses import dataclass

# Mainnet slugs — explicitly rejected (helps surface a clear error).
MAINNET_NETWORK_SLUGS: frozenset[str] = frozenset(
    {"mainnet", "ethereum", "polygon", "arbitrum", "optimism", "base"}
)


@dataclass(frozen=True, slots=True)
class NetworkInfo:
    slug: str
    chain_id: int
    explorer_tx_template: str  # e.g. "https://sepolia.etherscan.io/tx/{hash}"
    # Map of asset symbol → ERC-20 contract address (None means "not supported on this network").
    erc20_contracts: dict[str, str]


# Circle-issued USDC contract addresses (per Circle docs):
#   Sepolia          0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238
#   Arbitrum Sepolia 0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d
#   Base Sepolia     0x036CbD53842c5426634e7929541eC2318f3dCF7e
#   Polygon Amoy     0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582
# Holesky has no Circle USDC at time of writing; document the gap and reject the asset.
# USDT on testnets is inconsistent — we don't ship it for v1.
_NETWORKS: dict[str, NetworkInfo] = {
    "sepolia": NetworkInfo(
        slug="sepolia",
        chain_id=11155111,
        explorer_tx_template="https://sepolia.etherscan.io/tx/{hash}",
        erc20_contracts={"USDC": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"},
    ),
    "holesky": NetworkInfo(
        slug="holesky",
        chain_id=17000,
        explorer_tx_template="https://holesky.etherscan.io/tx/{hash}",
        erc20_contracts={},
    ),
    "polygon-amoy": NetworkInfo(
        slug="polygon-amoy",
        chain_id=80002,
        explorer_tx_template="https://amoy.polygonscan.com/tx/{hash}",
        erc20_contracts={"USDC": "0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582"},
    ),
    "arbitrum-sepolia": NetworkInfo(
        slug="arbitrum-sepolia",
        chain_id=421614,
        explorer_tx_template="https://sepolia.arbiscan.io/tx/{hash}",
        erc20_contracts={"USDC": "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d"},
    ),
    "base-sepolia": NetworkInfo(
        slug="base-sepolia",
        chain_id=84532,
        explorer_tx_template="https://sepolia.basescan.org/tx/{hash}",
        erc20_contracts={"USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"},
    ),
}


SUPPORTED_NETWORKS: frozenset[str] = frozenset(_NETWORKS.keys())


def get_network(slug: str) -> NetworkInfo | None:
    return _NETWORKS.get(slug)
