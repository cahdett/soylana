from pydantic import BaseModel
from typing import Optional, Union


class Token(BaseModel):
    """Token basic information."""

    address: str
    name: Optional[str] = None
    ticker: Optional[str] = None
    symbol: Optional[str] = None  # API might use 'symbol' instead of 'ticker'
    network: Optional[str] = None
    chain: Optional[str] = None  # API might use 'chain' instead of 'network'
    decimals: Optional[int] = None
    supply: Optional[Union[str, int, float]] = None  # Can be string or number
    total_supply: Optional[Union[str, int, float]] = None  # Can be string or number

    class Config:
        extra = "allow"


class TokenStats(BaseModel):
    """Token distribution statistics."""

    hhi: Optional[float] = None  # Herfindahl-Hirschman Index
    gini: Optional[float] = None  # Gini coefficient
    median_holder_position: Optional[int] = None
    avg_time_held: Optional[int] = None  # In seconds
    retention_rate: Optional[float] = None

    class Config:
        extra = "allow"


class TokenPnL(BaseModel):
    """Token aggregated profit/loss statistics."""

    break_even_price: Optional[float] = None
    realized_pnl_total: Optional[float] = None  # USD
    unrealized_pnl_total: Optional[float] = None  # USD

    class Config:
        extra = "allow"


class WalletCategories(BaseModel):
    """Breakdown of top holders by holding duration category."""

    diamond: Optional[int] = None  # Long-term holders
    gold: Optional[int] = None
    silver: Optional[int] = None
    bronze: Optional[int] = None
    wood: Optional[int] = None  # Newest holders
    new_holders: Optional[int] = None

    class Config:
        extra = "allow"


class SupplyBreakdown(BaseModel):
    """Token supply held by each wallet category."""

    diamond: Optional[float] = None
    gold: Optional[float] = None
    silver: Optional[float] = None
    bronze: Optional[float] = None
    wood: Optional[float] = None

    class Config:
        extra = "allow"
