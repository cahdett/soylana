from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token basic information."""

    address: str
    name: str
    ticker: str
    network: str
    decimals: int
    supply: str


class TokenStats(BaseModel):
    """Token distribution statistics."""

    hhi: float  # Herfindahl-Hirschman Index
    gini: float  # Gini coefficient
    median_holder_position: int
    avg_time_held: Optional[int] = None  # In seconds
    retention_rate: Optional[float] = None


class TokenPnL(BaseModel):
    """Token aggregated profit/loss statistics."""

    break_even_price: Optional[float] = None
    realized_pnl_total: float  # USD
    unrealized_pnl_total: float  # USD


class WalletCategories(BaseModel):
    """Breakdown of top holders by holding duration category."""

    diamond: int  # Long-term holders
    gold: int
    silver: int
    bronze: int
    wood: int  # Newest holders
    new_holders: int


class SupplyBreakdown(BaseModel):
    """Token supply held by each wallet category."""

    diamond: float
    gold: float
    silver: float
    bronze: float
    wood: float
