import httpx
from typing import Optional
from ..models import (
    Token,
    TokenStats,
    TokenPnL,
    WalletCategories,
    SupplyBreakdown,
    HolderList,
    HolderDeltas,
    HolderBreakdowns,
    WalletStats,
    Holder,
)
from ..models.holder import HolderCategories, HoldingBreakdown


class HolderScanError(Exception):
    """Base exception for HolderScan API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class HolderScanClient:
    """Async client for interacting with the HolderScan API."""

    def __init__(self, api_key: str, base_url: str = "https://api.holderscan.com/v0"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"x-api-key": self.api_key},
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an API request."""
        client = await self._get_client()
        response = await client.request(method, path, **kwargs)

        if response.status_code != 200:
            raise HolderScanError(
                f"API request failed: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    # ==================== Token Endpoints ====================

    async def list_tokens(
        self, chain: str = "sol", limit: int = 50, offset: int = 0
    ) -> tuple[int, list[Token]]:
        """
        List available tokens.

        Args:
            chain: Blockchain (sol or eth)
            limit: Results per page (max 100)
            offset: Pagination offset

        Returns:
            Tuple of (total count, list of tokens)
        """
        data = await self._request(
            "GET",
            f"/{chain}/tokens",
            params={"limit": min(limit, 100), "offset": offset},
        )
        tokens = [Token(**t) for t in data.get("tokens", [])]
        return data.get("total", 0), tokens

    async def get_token(self, token_address: str, chain: str = "sol") -> Token:
        """
        Get token details.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)

        Returns:
            Token information
        """
        data = await self._request("GET", f"/{chain}/tokens/{token_address}")
        return Token(**data)

    async def get_token_stats(
        self, token_address: str, chain: str = "sol"
    ) -> TokenStats:
        """
        Get token distribution statistics.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)

        Returns:
            Token statistics (HHI, Gini, etc.)
        """
        data = await self._request("GET", f"/{chain}/tokens/{token_address}/stats")
        return TokenStats(**data)

    async def get_token_pnl(self, token_address: str, chain: str = "sol") -> TokenPnL:
        """
        Get token aggregated PnL statistics.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)

        Returns:
            Token PnL data
        """
        data = await self._request("GET", f"/{chain}/tokens/{token_address}/stats/pnl")
        return TokenPnL(**data)

    async def get_wallet_categories(
        self, token_address: str, chain: str = "sol"
    ) -> WalletCategories:
        """
        Get token holder wallet categories.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)

        Returns:
            Breakdown of holders by category
        """
        data = await self._request(
            "GET", f"/{chain}/tokens/{token_address}/stats/wallet-categories"
        )
        return WalletCategories(**data)

    async def get_supply_breakdown(
        self, token_address: str, chain: str = "sol"
    ) -> SupplyBreakdown:
        """
        Get token supply breakdown by holder category.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)

        Returns:
            Supply held by each category
        """
        data = await self._request(
            "GET", f"/{chain}/tokens/{token_address}/stats/supply-breakdown"
        )
        return SupplyBreakdown(**data)

    # ==================== Holder Endpoints ====================

    async def get_holders(
        self,
        token_address: str,
        chain: str = "sol",
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> HolderList:
        """
        Get paginated list of token holders.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)
            min_amount: Minimum token amount filter
            max_amount: Maximum token amount filter
            limit: Results per page (max 100)
            offset: Pagination offset

        Returns:
            Paginated holder list
        """
        params = {"limit": min(limit, 100), "offset": offset}
        if min_amount is not None:
            params["min_amount"] = min_amount
        if max_amount is not None:
            params["max_amount"] = max_amount

        data = await self._request(
            "GET", f"/{chain}/tokens/{token_address}/holders", params=params
        )

        holders = [Holder(**h) for h in data.get("holders", [])]
        return HolderList(
            holder_count=data.get("holder_count", 0),
            total=data.get("total", 0),
            holders=holders,
        )

    async def get_holder_deltas(
        self, token_address: str, chain: str = "sol"
    ) -> HolderDeltas:
        """
        Get holder count changes over time periods.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)

        Returns:
            Holder deltas for various time periods
        """
        data = await self._request(
            "GET", f"/{chain}/tokens/{token_address}/holders/deltas"
        )
        return HolderDeltas.from_api_response(data)

    async def get_holder_breakdowns(
        self, token_address: str, chain: str = "sol"
    ) -> HolderBreakdowns:
        """
        Get holder statistics by holding value.

        Args:
            token_address: Token contract address
            chain: Blockchain (sol or eth)

        Returns:
            Holder breakdown by value tiers
        """
        data = await self._request(
            "GET", f"/{chain}/tokens/{token_address}/holders/breakdowns"
        )

        categories = HolderCategories(**data.get("categories", {}))
        return HolderBreakdowns(
            total_holders=data.get("total_holders", 0),
            holders_over_10_usd=data.get("holders_over_10_usd", 0),
            holders_over_100_usd=data.get("holders_over_100_usd", 0),
            holders_over_1000_usd=data.get("holders_over_1000_usd", 0),
            holders_over_10000_usd=data.get("holders_over_10000_usd", 0),
            holders_over_100k_usd=data.get("holders_over_100k_usd", 0),
            holders_over_1m_usd=data.get("holders_over_1m_usd", 0),
            categories=categories,
        )

    async def get_wallet_stats(
        self, token_address: str, wallet_address: str, chain: str = "sol"
    ) -> WalletStats:
        """
        Get statistics for a specific wallet's token holdings.

        Args:
            token_address: Token contract address
            wallet_address: Wallet address to analyze
            chain: Blockchain (sol or eth)

        Returns:
            Wallet-specific statistics
        """
        data = await self._request(
            "GET", f"/{chain}/tokens/{token_address}/stats/{wallet_address}"
        )

        # Handle case where holding_breakdown is None or missing
        holding_breakdown_data = data.get("holding_breakdown")
        if holding_breakdown_data is None:
            holding_breakdown = HoldingBreakdown(
                diamond=0, gold=0, silver=0, bronze=0, wood=0
            )
        else:
            holding_breakdown = HoldingBreakdown(**holding_breakdown_data)

        return WalletStats(
            amount=data.get("amount", 0),
            holder_category=data.get("holder_category", "unknown"),
            avg_time_held=data.get("avg_time_held"),
            holding_breakdown=holding_breakdown,
            unrealized_pnl=data.get("unrealized_pnl", 0),
            realized_pnl=data.get("realized_pnl", 0),
        )
