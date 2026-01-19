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


@router.post("/cross-checker")
async def cross_check_wallets(
    token_addresses: List[str] = Body(..., description="List of token addresses to cross-check"),
    min_usd_value: Optional[float] = Body(None, description="Minimum USD value held across all tokens"),
    max_holders_per_token: int = Body(1000, description="Max holders to fetch per token (higher = slower but more complete)"),
):
    """
    Find wallets that hold ALL of the specified tokens.

    This endpoint fetches holders for each token and finds the intersection -
    wallets that appear in every token's holder list.

    Args:
        token_addresses: List of token contract addresses (2-10 tokens)
        min_usd_value: Optional minimum USD value filter
        max_holders_per_token: Maximum holders to fetch per token (default 1000)

    Returns:
        List of common wallets with their holdings for each token
    """
    # Validate input
    if len(token_addresses) < 2:
        raise HTTPException(status_code=400, detail="At least 2 token addresses are required")
    if len(token_addresses) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 tokens allowed per cross-check")

    # Remove duplicates while preserving order
    token_addresses = list(dict.fromkeys(token_addresses))

    client = get_client()

    try:
        logger.info(f"Cross-checking {len(token_addresses)} tokens")

        # Store token info and holders for each token
        token_data = {}
        all_holder_sets = []

        # Fetch holders for each token
        for token_address in token_addresses:
            logger.info(f"Fetching holders for token: {token_address}")

            # Get token info first
            try:
                token_info = await client.get_token(token_address)
                token_name = token_info.name or token_info.symbol or token_address[:8]
                token_decimals = token_info.decimals or 0
            except Exception as e:
                logger.warning(f"Could not get token info for {token_address}: {e}")
                token_name = token_address[:8]
                token_decimals = 0

            # Fetch holders (paginate to get more)
            all_holders = {}
            offset = 0
            batch_size = 100

            while offset < max_holders_per_token:
                try:
                    holder_response = await client.get_holders(
                        token_address,
                        limit=batch_size,
                        offset=offset,
                    )

                    if not holder_response.holders:
                        break

                    for holder in holder_response.holders:
                        all_holders[holder.address] = {
                            "amount": holder.amount or 0,
                            "rank": holder.rank or 0,
                        }

                    offset += batch_size

                    # Stop if we got fewer than requested (no more data)
                    if len(holder_response.holders) < batch_size:
                        break

                except Exception as e:
                    logger.warning(f"Error fetching holders at offset {offset}: {e}")
                    break

            logger.info(f"Found {len(all_holders)} holders for {token_name}")

            token_data[token_address] = {
                "name": token_name,
                "decimals": token_decimals,
                "holders": all_holders,
                "total_holders_fetched": len(all_holders),
            }

            all_holder_sets.append(set(all_holders.keys()))

        # Find intersection of all holder sets
        if not all_holder_sets:
            return {
                "common_wallets": [],
                "tokens": token_data,
                "total_common": 0,
            }

        common_wallets = all_holder_sets[0]
        for holder_set in all_holder_sets[1:]:
            common_wallets = common_wallets.intersection(holder_set)

        logger.info(f"Found {len(common_wallets)} wallets holding all {len(token_addresses)} tokens")

        # Build result with holdings for each wallet
        result_wallets = []

        for wallet_address in common_wallets:
            wallet_holdings = {}
            total_value = 0  # We don't have price data yet, but structure supports it

            for token_address, data in token_data.items():
                holder_info = data["holders"].get(wallet_address, {})
                amount = holder_info.get("amount", 0)
                decimals = data["decimals"]

                # Adjust for decimals
                adjusted_amount = amount / (10 ** decimals) if decimals > 0 else amount

                wallet_holdings[token_address] = {
                    "token_name": data["name"],
                    "raw_amount": amount,
                    "adjusted_amount": adjusted_amount,
                    "rank": holder_info.get("rank", 0),
                }

            result_wallets.append({
                "wallet_address": wallet_address,
                "holdings": wallet_holdings,
                "tokens_held": len(wallet_holdings),
            })

        # Sort by average rank (lower is better - means bigger holder)
        def avg_rank(wallet):
            ranks = [h["rank"] for h in wallet["holdings"].values() if h["rank"] > 0]
            return sum(ranks) / len(ranks) if ranks else float("inf")

        result_wallets.sort(key=avg_rank)

        # Build token summary
        token_summary = []
        for addr in token_addresses:
            data = token_data[addr]
            token_summary.append({
                "address": addr,
                "name": data["name"],
                "decimals": data["decimals"],
                "holders_fetched": data["total_holders_fetched"],
            })

        return {
            "common_wallets": result_wallets,
            "tokens": token_summary,
            "total_common": len(result_wallets),
            "query": {
                "token_count": len(token_addresses),
                "max_holders_per_token": max_holders_per_token,
                "min_usd_value": min_usd_value,
            },
        }

    except HolderScanError as e:
        logger.error(f"HolderScan error in cross-checker: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in cross-checker: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


# ==================== Health Check ====================


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
