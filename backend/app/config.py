from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Public testnet RPCs (override per env-var if you have a private one).
# All values are HTTPS JSON-RPC endpoints.
_DEFAULT_RPC_URLS: dict[str, str] = {
    "sepolia": "https://ethereum-sepolia-rpc.publicnode.com",
    "holesky": "https://ethereum-holesky-rpc.publicnode.com",
    "polygon-amoy": "https://polygon-amoy-bor-rpc.publicnode.com",
    "arbitrum-sepolia": "https://arbitrum-sepolia-rpc.publicnode.com",
    "base-sepolia": "https://base-sepolia-rpc.publicnode.com",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = "dev"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pampa"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5"
    wallbit_api_key: str = ""
    wallbit_base_url: str = "https://api.wallbit.io"

    # Per-network Ethereum JSON-RPC URLs. Each maps an env var to a network slug
    # used by /connections/ethereum-custodial/* and /onchain/*.
    ethereum_rpc_url_sepolia: str = _DEFAULT_RPC_URLS["sepolia"]
    ethereum_rpc_url_holesky: str = _DEFAULT_RPC_URLS["holesky"]
    ethereum_rpc_url_polygon_amoy: str = _DEFAULT_RPC_URLS["polygon-amoy"]
    ethereum_rpc_url_arbitrum_sepolia: str = _DEFAULT_RPC_URLS["arbitrum-sepolia"]
    ethereum_rpc_url_base_sepolia: str = _DEFAULT_RPC_URLS["base-sepolia"]

    fernet_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ethereum_rpc_urls(self) -> dict[str, str]:
        return {
            "sepolia": self.ethereum_rpc_url_sepolia,
            "holesky": self.ethereum_rpc_url_holesky,
            "polygon-amoy": self.ethereum_rpc_url_polygon_amoy,
            "arbitrum-sepolia": self.ethereum_rpc_url_arbitrum_sepolia,
            "base-sepolia": self.ethereum_rpc_url_base_sepolia,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
