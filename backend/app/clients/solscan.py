import httpx
import asyncio
import logging
from typing import Optional, List, Set
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SolscanError(Exception):
    """Base exception for Solscan API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class TokenTransfer(BaseModel):
    """Token transfer record."""

    signature: Optional[str] = None
    block_time: Optional[int] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    amount: Optional[float] = None
    token_address: Optional[str] = None
    # Additional fields from Solscan
    trans_id: Optional[str] = None
    time: Optional[int] = None

    class Config:
        extra = "allow"


class AccountDetail(BaseModel):
    """Account/wallet details."""

    address: Optional[str] = None
    lamports: Optional[int] = None
    owner_program: Optional[str] = None
    account_type: Optional[str] = None

    class Config:
        extra = "allow"


class SolscanClient:
    """Async client for interacting with the Solscan Pro API v2."""

    def __init__(self, api_key: str, base_url: str = "https://pro-api.solscan.io/v2.0"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"token": self.api_key},
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
            raise SolscanError(
                f"API request failed: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def get_token_holders(
        self,
        token_address: str,
        page: int = 1,
        page_size: int = 100,
    ) -> dict:
        """
        Get token holders.

        Args:
            token_address: Token mint address
            page: Page number
            page_size: Results per page (max 100)

        Returns:
            Holder data including addresses and amounts
        """
        data = await self._request(
            "GET",
            "/token/holders",
            params={
                "address": token_address,
                "page": page,
                "page_size": min(page_size, 100),
            },
        )
        return data

    async def get_token_transfers(
        self,
        token_address: str,
        page: int = 1,
        page_size: int = 100,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        sort_by: str = "block_time",
        sort_order: str = "desc",
    ) -> dict:
        """
        Get token transfer history.

        Args:
            token_address: Token mint address
            page: Page number
            page_size: Results per page
            from_time: Start timestamp (Unix seconds)
            to_time: End timestamp (Unix seconds)
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Transfer history
        """
        params = {
            "address": token_address,
            "page": page,
            "page_size": min(page_size, 100),
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if from_time is not None:
            params["block_time[]"] = from_time
        if to_time is not None:
            params["block_time[]="] = to_time

        data = await self._request(
            "GET",
            "/token/transfer",
            params=params,
        )
        return data

    async def get_all_token_traders(
        self,
        token_address: str,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        max_pages: int = 50,
    ) -> Set[str]:
        """
        Get all unique wallet addresses that have traded a token within a timeframe.

        Args:
            token_address: Token mint address
            from_time: Start timestamp (Unix seconds)
            to_time: End timestamp (Unix seconds)
            max_pages: Maximum pages to fetch (100 transfers per page)

        Returns:
            Set of unique wallet addresses that traded the token
        """
        traders: Set[str] = set()
        page = 1

        while page <= max_pages:
            try:
                data = await self.get_token_transfers(
                    token_address=token_address,
                    page=page,
                    page_size=100,
                    from_time=from_time,
                    to_time=to_time,
                )

                transfers = data.get("data", [])
                if not transfers:
                    break

                for transfer in transfers:
                    # Get both sender and receiver addresses
                    from_addr = transfer.get("from_address")
                    to_addr = transfer.get("to_address")

                    if from_addr and from_addr != "11111111111111111111111111111111":
                        traders.add(from_addr)
                    if to_addr and to_addr != "11111111111111111111111111111111":
                        traders.add(to_addr)

                # Check if there are more pages
                if len(transfers) < 100:
                    break

                page += 1
                # Rate limit: small delay between requests
                await asyncio.sleep(0.1)

            except SolscanError as e:
                logger.warning(f"Error fetching transfers page {page} for {token_address}: {e}")
                break

        logger.info(f"Found {len(traders)} unique traders for {token_address} across {page} pages")
        return traders

    async def get_account_detail(self, address: str) -> AccountDetail:
        """
        Get account/wallet details.

        Args:
            address: Wallet address

        Returns:
            Account details
        """
        data = await self._request(
            "GET",
            "/account/detail",
            params={"address": address},
        )
        return AccountDetail(**data.get("data", {}))

    async def get_account_transfers(
        self,
        address: str,
        token_address: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict:
        """
        Get account transfer history.

        Args:
            address: Wallet address
            token_address: Optional token filter
            page: Page number
            page_size: Results per page

        Returns:
            Transfer history for the account
        """
        params = {
            "address": address,
            "page": page,
            "page_size": min(page_size, 100),
        }
        if token_address:
            params["token"] = token_address

        data = await self._request("GET", "/account/transfer", params=params)
        return data

    async def get_account_token_accounts(self, address: str) -> dict:
        """
        Get all token accounts for a wallet.

        Args:
            address: Wallet address

        Returns:
            List of token accounts and balances
        """
        data = await self._request(
            "GET",
            "/account/token-accounts",
            params={"address": address},
        )
        return data

    async def get_token_price(self, token_address: str) -> dict:
        """
        Get token price.

        Args:
            token_address: Token mint address

        Returns:
            Price data
        """
        data = await self._request(
            "GET",
            "/token/price",
            params={"address": token_address},
        )
        return data
