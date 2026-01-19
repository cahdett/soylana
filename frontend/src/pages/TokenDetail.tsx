import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getTokenAnalysis, getHolders, getWalletStats } from '../api/client';
import {
  StatCard,
  HolderDeltasChart,
  HolderDistributionChart,
  TopHoldersTable,
  ValueBreakdownChart,
  WalletAnalysisCard,
} from '../components';
import type { WalletStats } from '../types';

export function TokenDetail() {
  const { address } = useParams<{ address: string }>();
  const navigate = useNavigate();
  const [selectedWallet, setSelectedWallet] = useState<string | null>(null);
  const [walletStats, setWalletStats] = useState<WalletStats | null>(null);
  const [walletLoading, setWalletLoading] = useState(false);

  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['tokenAnalysis', address],
    queryFn: () => getTokenAnalysis(address!),
    enabled: !!address,
  });

  const { data: holders } = useQuery({
    queryKey: ['holders', address],
    queryFn: () => getHolders(address!, { limit: 20 }),
    enabled: !!address,
  });

  useEffect(() => {
    if (selectedWallet && address) {
      setWalletLoading(true);
      getWalletStats(address, selectedWallet)
        .then(setWalletStats)
        .catch(console.error)
        .finally(() => setWalletLoading(false));
    }
  }, [selectedWallet, address]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading token analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-xl mb-4">Failed to load token data</div>
          <p className="text-gray-400 mb-4">
            {error instanceof Error ? error.message : 'Token not found or API error'}
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
          >
            Back to Search
          </button>
        </div>
      </div>
    );
  }

  const { token, stats, holder_deltas, holder_breakdowns, pnl } = analysis;

  // Safe accessors with defaults
  const totalHolders = holder_breakdowns?.total_holders ?? 0;
  const dayChange = holder_deltas?.day_1 ?? 0;
  const hhi = stats?.hhi ?? 0;
  const gini = stats?.gini ?? 0;
  const whaleCount = holder_breakdowns?.categories?.whale ?? 0;
  const tokenName = token?.name || token?.symbol || 'Unknown Token';
  const tokenTicker = token?.ticker || token?.symbol || '???';
  const tokenSupply = token?.supply ?? token?.total_supply ?? 0;
  const tokenDecimals = token?.decimals ?? 0;

  const formatNumber = (n: number, decimals = 2) => {
    if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(decimals)}B`;
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(decimals)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(decimals)}K`;
    return n.toFixed(decimals);
  };

  const safeParseSupply = () => {
    try {
      const supply = typeof tokenSupply === 'string' ? parseInt(tokenSupply) : Number(tokenSupply);
      const divisor = Math.pow(10, tokenDecimals);
      return formatNumber(supply / divisor);
    } catch {
      return 'N/A';
    }
  };

  // Default categories if missing
  const categories = holder_breakdowns?.categories ?? {
    whale: 0,
    dolphin: 0,
    fish: 0,
    crab: 0,
    shrimp: 0,
  };

  // Default deltas if missing
  const deltas = {
    hour_1: holder_deltas?.hour_1 ?? 0,
    hours_2: holder_deltas?.hours_2 ?? 0,
    hours_4: holder_deltas?.hours_4 ?? 0,
    hours_12: holder_deltas?.hours_12 ?? 0,
    day_1: holder_deltas?.day_1 ?? 0,
    days_3: holder_deltas?.days_3 ?? 0,
    days_7: holder_deltas?.days_7 ?? 0,
    days_14: holder_deltas?.days_14 ?? 0,
    days_30: holder_deltas?.days_30 ?? 0,
  };

  // Default breakdowns if missing
  const breakdowns = {
    total_holders: holder_breakdowns?.total_holders ?? 0,
    holders_over_10_usd: holder_breakdowns?.holders_over_10_usd ?? 0,
    holders_over_100_usd: holder_breakdowns?.holders_over_100_usd ?? 0,
    holders_over_1000_usd: holder_breakdowns?.holders_over_1000_usd ?? 0,
    holders_over_10000_usd: holder_breakdowns?.holders_over_10000_usd ?? 0,
    holders_over_100k_usd: holder_breakdowns?.holders_over_100k_usd ?? 0,
    holders_over_1m_usd: holder_breakdowns?.holders_over_1m_usd ?? 0,
    categories,
  };

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="text-gray-400 hover:text-white mb-4 flex items-center gap-2"
        >
          ← Back to Search
        </button>
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">{tokenName}</h1>
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-purple-400 font-semibold">${tokenTicker}</span>
              <span>•</span>
              <span className="font-mono text-sm">
                {token?.address ? `${token.address.slice(0, 8)}...${token.address.slice(-8)}` : address}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
        <StatCard
          label="Total Holders"
          value={formatNumber(totalHolders, 0)}
        />
        <StatCard
          label="24h Change"
          value={dayChange >= 0 ? `+${dayChange}` : dayChange.toString()}
          trend={dayChange > 0 ? 'up' : dayChange < 0 ? 'down' : 'neutral'}
        />
        <StatCard
          label="HHI Index"
          value={hhi.toFixed(4)}
          subValue={hhi < 0.01 ? 'Highly Distributed' : hhi < 0.1 ? 'Moderate' : 'Concentrated'}
        />
        <StatCard
          label="Gini Coefficient"
          value={gini.toFixed(4)}
          subValue={gini < 0.5 ? 'Equal' : gini < 0.8 ? 'Moderate' : 'Unequal'}
        />
        <StatCard
          label="Whales"
          value={whaleCount.toLocaleString()}
        />
        <StatCard
          label="Supply"
          value={safeParseSupply()}
        />
      </div>

      {/* PnL Stats (if available) */}
      {pnl && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <StatCard
            label="Break Even Price"
            value={pnl.break_even_price ? `$${pnl.break_even_price.toFixed(6)}` : 'N/A'}
          />
          <StatCard
            label="Total Realized PnL"
            value={`$${formatNumber(pnl.realized_pnl_total ?? 0)}`}
            trend={(pnl.realized_pnl_total ?? 0) >= 0 ? 'up' : 'down'}
          />
          <StatCard
            label="Total Unrealized PnL"
            value={`$${formatNumber(pnl.unrealized_pnl_total ?? 0)}`}
            trend={(pnl.unrealized_pnl_total ?? 0) >= 0 ? 'up' : 'down'}
          />
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <HolderDeltasChart deltas={deltas} />
        <HolderDistributionChart categories={categories} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ValueBreakdownChart breakdowns={breakdowns} />
        {holders && (
          <TopHoldersTable
            holders={holders.holders}
            totalSupply={typeof tokenSupply === 'string' ? parseInt(tokenSupply) : Number(tokenSupply)}
            decimals={tokenDecimals}
            onWalletClick={(addr) => setSelectedWallet(addr)}
          />
        )}
      </div>

      {/* Wallet Analysis Modal */}
      {selectedWallet && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-lg w-full p-6 relative">
            <button
              onClick={() => {
                setSelectedWallet(null);
                setWalletStats(null);
              }}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              ✕
            </button>
            {walletLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
                <p className="text-gray-400">Loading wallet data...</p>
              </div>
            ) : walletStats ? (
              <WalletAnalysisCard
                stats={walletStats}
                walletAddress={selectedWallet}
                tokenTicker={tokenTicker}
              />
            ) : (
              <div className="text-center py-8 text-red-400">
                Failed to load wallet data
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
