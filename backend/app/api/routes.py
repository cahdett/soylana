from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..clients import HolderScanClient
from ..clients.holderscan import HolderScanError
from ..config import get_settings

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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        # Fetch all data in parallel-ish manner
        token = await client.get_token(token_address)
        stats = await client.get_token_stats(token_address)
        holder_deltas = await client.get_holder_deltas(token_address)
        holder_breakdowns = await client.get_holder_breakdowns(token_address)

        # Try to get PnL data (might not be available for all tokens)
        try:
            pnl = await client.get_token_pnl(token_address)
            pnl_data = pnl.model_dump()
        except HolderScanError:
            pnl_data = None

        # Try to get wallet categories
        try:
            wallet_cats = await client.get_wallet_categories(token_address)
            wallet_cats_data = wallet_cats.model_dump()
        except HolderScanError:
            wallet_cats_data = None

        # Try to get supply breakdown
        try:
            supply = await client.get_supply_breakdown(token_address)
            supply_data = supply.model_dump()
        except HolderScanError:
            supply_data = None

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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
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
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    finally:
        await client.close()


# ==================== Health Check ====================


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
