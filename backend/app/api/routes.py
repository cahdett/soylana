from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List
import logging
from ..clients import HolderScanClient, SolscanClient
from ..clients.holderscan import HolderScanError
from ..clients.solscan import SolscanError
from ..config import get_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tokens"])


def get_client() -> HolderScanClient:
    """Get HolderScan client instance."""
    settings = get_settings()
    return HolderScanClient(
        api_key=settings.holderscan_api_key,
        base_url=settings.holderscan_base_url,
    )


# ==================== Token Endpoints ====================


@router.get("/tokens")
async def list_tokens(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List available tokens."""
    client = get_client()
    try:
        total, tokens = await client.list_tokens(chain="sol", limit=limit, offset=offset)
        return {"total": total, "tokens": [t.model_dump() for t in tokens]}
    except HolderScanError as e:
        logger.error(f"HolderScan error: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}")
async def get_token(token_address: str):
    """Get token details."""
    client = get_client()
    try:
        token = await client.get_token(token_address)
        return token.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for token {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for token {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}/stats")
async def get_token_stats(token_address: str):
    """Get token distribution statistics (HHI, Gini, etc.)."""
    client = get_client()
    try:
        stats = await client.get_token_stats(token_address)
        return stats.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for stats {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for stats {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}/pnl")
async def get_token_pnl(token_address: str):
    """Get token aggregated PnL statistics."""
    client = get_client()
    try:
        pnl = await client.get_token_pnl(token_address)
        return pnl.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for pnl {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for pnl {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}/wallet-categories")
async def get_wallet_categories(token_address: str):
    """Get token holder wallet categories breakdown."""
    client = get_client()
    try:
        categories = await client.get_wallet_categories(token_address)
        return categories.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for wallet-categories {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for wallet-categories {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}/supply-breakdown")
async def get_supply_breakdown(token_address: str):
    """Get token supply breakdown by holder category."""
    client = get_client()
    try:
        breakdown = await client.get_supply_breakdown(token_address)
        return breakdown.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for supply-breakdown {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for supply-breakdown {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}/analysis")
async def get_full_token_analysis(token_address: str):
    """
    Get comprehensive token analysis combining all available data.
    This is the main endpoint for token analysis.
    """
    client = get_client()
    try:
        logger.info(f"Fetching analysis for token: {token_address}")

        # Fetch all data
        token = await client.get_token(token_address)
        logger.info(f"Got token data")

        stats = await client.get_token_stats(token_address)
        logger.info(f"Got stats data")

        holder_deltas = await client.get_holder_deltas(token_address)
        logger.info(f"Got holder deltas")

        holder_breakdowns = await client.get_holder_breakdowns(token_address)
        logger.info(f"Got holder breakdowns")

        # Try to get PnL data (might not be available for all tokens)
        pnl_data = None
        try:
            pnl = await client.get_token_pnl(token_address)
            pnl_data = pnl.model_dump()
        except Exception as e:
            logger.info(f"PnL data not available: {e}")

        # Try to get wallet categories
        wallet_cats_data = None
        try:
            wallet_cats = await client.get_wallet_categories(token_address)
            wallet_cats_data = wallet_cats.model_dump()
        except Exception as e:
            logger.info(f"Wallet categories not available: {e}")

        # Try to get supply breakdown
        supply_data = None
        try:
            supply = await client.get_supply_breakdown(token_address)
            supply_data = supply.model_dump()
        except Exception as e:
            logger.info(f"Supply breakdown not available: {e}")

        return {
            "token": token.model_dump(),
            "stats": stats.model_dump(),
            "holder_deltas": holder_deltas.model_dump(),
            "holder_breakdowns": holder_breakdowns.model_dump(),
            "pnl": pnl_data,
            "wallet_categories": wallet_cats_data,
            "supply_breakdown": supply_data,
        }
    except HolderScanError as e:
        logger.error(f"HolderScan error for analysis {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for analysis {token_address}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


# ==================== Holder Endpoints ====================


@router.get("/tokens/{token_address}/holders")
async def get_holders(
    token_address: str,
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get paginated list of token holders."""
    client = get_client()
    try:
        holders = await client.get_holders(
            token_address,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset,
        )
        return holders.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for holders {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for holders {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}/holders/deltas")
async def get_holder_deltas(token_address: str):
    """Get holder count changes over various time periods."""
    client = get_client()
    try:
        deltas = await client.get_holder_deltas(token_address)
        return deltas.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for deltas {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for deltas {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/tokens/{token_address}/holders/breakdowns")
async def get_holder_breakdowns(token_address: str):
    """Get holder statistics by holding value."""
    client = get_client()
    try:
        breakdowns = await client.get_holder_breakdowns(token_address)
        return breakdowns.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for breakdowns {token_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for breakdowns {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


# ==================== Wallet Analysis Endpoints ====================


@router.get("/tokens/{token_address}/wallet/{wallet_address}")
async def get_wallet_stats(token_address: str, wallet_address: str):
    """Get statistics for a specific wallet's token holdings."""
    client = get_client()
    try:
        stats = await client.get_wallet_stats(token_address, wallet_address)
        return stats.model_dump()
    except HolderScanError as e:
        logger.error(f"HolderScan error for wallet {wallet_address}: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for wallet {wallet_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


# ==================== Cross-Checker Endpoints ====================


def get_solscan_client() -> Optional[SolscanClient]:
    """Get Solscan client instance if API key is configured."""
    settings = get_settings()
    if not settings.solscan_api_key:
        return None
    return SolscanClient(
        api_key=settings.solscan_api_key,
        base_url=settings.solscan_base_url,
    )


from pydantic import BaseModel


class TokenInput(BaseModel):
    """Input for a single token in cross-checker."""
    address: str
    from_time: Optional[int] = None  # Unix timestamp (seconds)
    to_time: Optional[int] = None  # Unix timestamp (seconds)


@router.post("/cross-checker")
async def cross_check_wallets(
    tokens: List[TokenInput] = Body(..., description="List of tokens with optional timeframe filters"),
    max_pages_per_token: int = Body(50, description="Max pages of transfers to fetch per token (100 transfers per page)"),
):
    """
    Find wallets that have TRADED ALL of the specified tokens within their timeframes.

    This endpoint fetches transfer history for each token using Solscan API and finds
    wallets that appear in the transfer history of ALL tokens.

    Args:
        tokens: List of token inputs, each containing:
            - address: Token contract address
            - from_time: Optional start timestamp (Unix seconds)
            - to_time: Optional end timestamp (Unix seconds)
        max_pages_per_token: Max pages of transfers to fetch (100 per page, default 50 = 5000 transfers)

    Returns:
        List of common wallets that traded all specified tokens
    """
    # Validate input
    if len(tokens) < 2:
        raise HTTPException(status_code=400, detail="At least 2 tokens are required")
    if len(tokens) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 tokens allowed per cross-check")

    solscan = get_solscan_client()
    if not solscan:
        raise HTTPException(status_code=500, detail="Solscan API key not configured")

    holderscan = get_client()

    try:
        logger.info(f"Cross-checking {len(tokens)} tokens for common traders")

        # Store token info and traders for each token
        token_data = {}
        all_trader_sets = []

        # Fetch traders for each token
        for token_input in tokens:
            token_address = token_input.address
            logger.info(f"Fetching traders for token: {token_address}")
            logger.info(f"  Timeframe: {token_input.from_time} to {token_input.to_time}")

            # Get token info from HolderScan
            token_name = token_address[:8]
            token_decimals = 0
            try:
                token_info = await holderscan.get_token(token_address)
                token_name = token_info.name or token_info.symbol or token_address[:8]
                token_decimals = token_info.decimals or 0
            except Exception as e:
                logger.warning(f"Could not get token info for {token_address}: {e}")

            # Fetch traders from Solscan
            traders = await solscan.get_all_token_traders(
                token_address=token_address,
                from_time=token_input.from_time,
                to_time=token_input.to_time,
                max_pages=max_pages_per_token,
            )

            logger.info(f"Found {len(traders)} unique traders for {token_name}")

            token_data[token_address] = {
                "name": token_name,
                "decimals": token_decimals,
                "traders": traders,
                "total_traders_found": len(traders),
                "from_time": token_input.from_time,
                "to_time": token_input.to_time,
            }

            all_trader_sets.append(traders)

        # Find intersection of all trader sets
        if not all_trader_sets:
            return {
                "common_wallets": [],
                "tokens": [],
                "total_common": 0,
            }

        common_traders = all_trader_sets[0]
        for trader_set in all_trader_sets[1:]:
            common_traders = common_traders.intersection(trader_set)

        logger.info(f"Found {len(common_traders)} wallets that traded all {len(tokens)} tokens")

        # Build result
        result_wallets = []
        for wallet_address in common_traders:
            wallet_tokens = {}
            for token_address, data in token_data.items():
                wallet_tokens[token_address] = {
                    "token_name": data["name"],
                    "traded": wallet_address in data["traders"],
                }
            result_wallets.append({
                "wallet_address": wallet_address,
                "tokens_traded": wallet_tokens,
            })

        # Sort alphabetically by wallet address for consistency
        result_wallets.sort(key=lambda w: w["wallet_address"])

        # Build token summary
        token_summary = []
        for token_input in tokens:
            addr = token_input.address
            data = token_data[addr]
            token_summary.append({
                "address": addr,
                "name": data["name"],
                "decimals": data["decimals"],
                "traders_found": data["total_traders_found"],
                "from_time": data["from_time"],
                "to_time": data["to_time"],
            })

        return {
            "common_wallets": result_wallets,
            "tokens": token_summary,
            "total_common": len(result_wallets),
            "query": {
                "token_count": len(tokens),
                "max_pages_per_token": max_pages_per_token,
            },
        }

    except SolscanError as e:
        logger.error(f"Solscan error in cross-checker: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in cross-checker: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await solscan.close()
        await holderscan.close()


# ==================== Health Check ====================


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
