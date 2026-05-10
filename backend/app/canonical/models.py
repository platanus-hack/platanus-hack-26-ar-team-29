from typing import Any

from pydantic import BaseModel, Field


class CanonicalBalance(BaseModel):
    provider: str
    account: str
    symbol: str
    currency: str
    amount: float
    usd_value: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class CanonicalPosition(BaseModel):
    provider: str
    account: str
    symbol: str
    shares: float
    current_price_usd: float | None = None
    usd_value: float | None = None
    avg_cost_usd: float | None = None
    cost_basis_usd: float | None = None
    unrealized_pnl_usd: float | None = None
    pnl_percentage: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
