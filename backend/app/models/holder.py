from pydantic import BaseModel
from typing import Optional


class Holder(BaseModel):
    """Individual token holder."""

    address: str
    spl_token_account: Optional[str] = None
    amount: float
    rank: int


class HolderList(BaseModel):
    """Paginated list of token holders."""

    holder_count: int
    total: int  # Total matching filter
    holders: list[Holder]


class HolderDeltas(BaseModel):
    """Holder count changes over different time periods."""

    hour_1: int
    hours_2: int
    hours_4: int
    hours_12: int
    day_1: int
    days_3: int
    days_7: int
    days_14: int
    days_30: int

    @classmethod
    def from_api_response(cls, data: dict) -> "HolderDeltas":
        """Parse API response with different key format."""
        return cls(
            hour_1=data.get("1hour", 0),
            hours_2=data.get("2hours", 0),
            hours_4=data.get("4hours", 0),
            hours_12=data.get("12hours", 0),
            day_1=data.get("1day", 0),
            days_3=data.get("3days", 0),
            days_7=data.get("7days", 0),
            days_14=data.get("14days", 0),
            days_30=data.get("30days", 0),
        )


class HolderCategories(BaseModel):
    """Holder count by value category."""

    shrimp: int  # Smallest holders
    crab: int
    fish: int
    dolphin: int
    whale: int  # Largest holders


class HolderBreakdowns(BaseModel):
    """Holder statistics organized by holding value."""

    total_holders: int
    holders_over_10_usd: int
    holders_over_100_usd: int
    holders_over_1000_usd: int
    holders_over_10000_usd: int
    holders_over_100k_usd: int
    holders_over_1m_usd: int
    categories: HolderCategories


class HoldingBreakdown(BaseModel):
    """Breakdown of a wallet's holdings by age."""

    diamond: float
    gold: float
    silver: float
    bronze: float
    wood: float


class WalletStats(BaseModel):
    """Statistics for a specific wallet's token holdings."""

    amount: float
    holder_category: str  # e.g., "whale", "dolphin", etc.
    avg_time_held: Optional[int] = None  # In seconds
    holding_breakdown: HoldingBreakdown
    unrealized_pnl: float  # USD
    realized_pnl: float  # USD
