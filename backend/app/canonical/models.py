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
    usd_value: float | None = None
    pnl_percentage: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
