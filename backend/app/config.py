import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

# Public testnet RPCs (override per env-var if you have a private one).
# All values are HTTPS JSON-RPC endpoints.
_DEFAULT_RPC_URLS: dict[str, str] = {
    "sepolia": "https://ethereum-sepolia-rpc.publicnode.com",
    "holesky": "https://ethereum-holesky-rpc.publicnode.com",
    "polygon-amoy": "https://polygon-amoy-bor-rpc.publicnode.com",
    "arbitrum-sepolia": "https://arbitrum-sepolia-rpc.publicnode.com",
    "base-sepolia": "https://base-sepolia-rpc.publicnode.com",
    "base": "https://base-rpc.publicnode.com",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = os.getenv("ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")

    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/atajo"
    )

    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
    anthropic_fallback_model: str = os.getenv(
        "ANTHROPIC_FALLBACK_MODEL", "claude-3-5-sonnet-20241022"
    )
    wallbit_api_key: str = os.getenv("WALLBIT_API_KEY", "")
    # The test key (`wlb_test_*`) only validates against the dev API; falling
    # back to prod silently returns 401 on every request. Default to MCP URL.
    wallbit_base_url: str = os.getenv(
        "WALLBIT_BASE_URL",
        os.getenv("WALLBIT_MCP_URL", "https://api.dev.wallbit.io"),
    )
    wallbit_mcp_url: str = os.getenv("WALLBIT_MCP_URL", "https://api.dev.wallbit.io")

    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))

    # Per-network Ethereum JSON-RPC URLs. Each maps an env var to a network slug
    # used by /connections/ethereum-custodial/* and /onchain/*.
    ethereum_rpc_url_sepolia: str = os.getenv(
        "ETHEREUM_RPC_URL_SEPOLIA", _DEFAULT_RPC_URLS["sepolia"]
    )
    ethereum_rpc_url_holesky: str = os.getenv(
        "ETHEREUM_RPC_URL_HOLESKY", _DEFAULT_RPC_URLS["holesky"]
    )
    ethereum_rpc_url_polygon_amoy: str = os.getenv(
        "ETHEREUM_RPC_URL_POLYGON_AMOY", _DEFAULT_RPC_URLS["polygon-amoy"]
    )
    ethereum_rpc_url_arbitrum_sepolia: str = os.getenv(
        "ETHEREUM_RPC_URL_ARBITRUM_SEPOLIA", _DEFAULT_RPC_URLS["arbitrum-sepolia"]
    )
    ethereum_rpc_url_base_sepolia: str = os.getenv(
        "ETHEREUM_RPC_URL_BASE_SEPOLIA", _DEFAULT_RPC_URLS["base-sepolia"]
    )
    ethereum_rpc_url_base: str = os.getenv("ETHEREUM_RPC_URL_BASE", _DEFAULT_RPC_URLS["base"])

    fernet_key: str = os.getenv("FERNET_KEY", "")

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
            "base": self.ethereum_rpc_url_base,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
