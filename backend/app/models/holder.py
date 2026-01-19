from pydantic import BaseModel
from typing import Optional


class Holder(BaseModel):
    """Individual token holder."""

    address: str
    spl_token_account: Optional[str] = None
    amount: Optional[float] = 0
    rank: Optional[int] = 0

    class Config:
        extra = "allow"


class HolderList(BaseModel):
    """Paginated list of token holders."""

    holder_count: Optional[int] = 0
    total: Optional[int] = 0  # Total matching filter
    holders: list[Holder] = []

    class Config:
        extra = "allow"


class HolderDeltas(BaseModel):
    """Holder count changes over different time periods."""

    hour_1: Optional[int] = 0
    hours_2: Optional[int] = 0
    hours_4: Optional[int] = 0
    hours_12: Optional[int] = 0
    day_1: Optional[int] = 0
    days_3: Optional[int] = 0
    days_7: Optional[int] = 0
    days_14: Optional[int] = 0
    days_30: Optional[int] = 0

    @classmethod
    def from_api_response(cls, data: dict) -> "HolderDeltas":
        """Parse API response with different key format."""
        return cls(
            hour_1=data.get("1hour", 0) or 0,
            hours_2=data.get("2hours", 0) or 0,
            hours_4=data.get("4hours", 0) or 0,
            hours_12=data.get("12hours", 0) or 0,
            day_1=data.get("1day", 0) or 0,
            days_3=data.get("3days", 0) or 0,
            days_7=data.get("7days", 0) or 0,
            days_14=data.get("14days", 0) or 0,
            days_30=data.get("30days", 0) or 0,
        )

    class Config:
        extra = "allow"


class HolderCategories(BaseModel):
    """Holder count by value category."""

    shrimp: Optional[int] = 0  # Smallest holders
    crab: Optional[int] = 0
    fish: Optional[int] = 0
    dolphin: Optional[int] = 0
    whale: Optional[int] = 0  # Largest holders

    class Config:
        extra = "allow"


class HolderBreakdowns(BaseModel):
    """Holder statistics organized by holding value."""

    total_holders: Optional[int] = 0
    holders_over_10_usd: Optional[int] = 0
    holders_over_100_usd: Optional[int] = 0
    holders_over_1000_usd: Optional[int] = 0
    holders_over_10000_usd: Optional[int] = 0
    holders_over_100k_usd: Optional[int] = 0
    holders_over_1m_usd: Optional[int] = 0
    categories: Optional[HolderCategories] = None

    class Config:
        extra = "allow"


class HoldingBreakdown(BaseModel):
    """Breakdown of a wallet's holdings by age."""

    diamond: Optional[float] = 0
    gold: Optional[float] = 0
    silver: Optional[float] = 0
    bronze: Optional[float] = 0
    wood: Optional[float] = 0

    class Config:
        extra = "allow"


class WalletStats(BaseModel):
    """Statistics for a specific wallet's token holdings."""

    amount: Optional[float] = 0
    holder_category: Optional[str] = "unknown"  # e.g., "whale", "dolphin", etc.
    avg_time_held: Optional[int] = None  # In seconds
    holding_breakdown: Optional[HoldingBreakdown] = None
    unrealized_pnl: Optional[float] = 0  # USD
    realized_pnl: Optional[float] = 0  # USD

    class Config:
        extra = "allow"
