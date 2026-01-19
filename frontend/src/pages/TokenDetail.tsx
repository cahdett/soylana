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

  const formatNumber = (n: number, decimals = 2) => {
    if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(decimals)}B`;
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(decimals)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(decimals)}K`;
    return n.toFixed(decimals);
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
            <h1 className="text-3xl font-bold">{token.name}</h1>
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-purple-400 font-semibold">${token.ticker}</span>
              <span>•</span>
              <span className="font-mono text-sm">
                {token.address.slice(0, 8)}...{token.address.slice(-8)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
        <StatCard
          label="Total Holders"
          value={formatNumber(holder_breakdowns.total_holders, 0)}
        />
        <StatCard
          label="24h Change"
          value={holder_deltas.day_1 >= 0 ? `+${holder_deltas.day_1}` : holder_deltas.day_1.toString()}
          trend={holder_deltas.day_1 > 0 ? 'up' : holder_deltas.day_1 < 0 ? 'down' : 'neutral'}
        />
        <StatCard
          label="HHI Index"
          value={stats.hhi.toFixed(4)}
          subValue={stats.hhi < 0.01 ? 'Highly Distributed' : stats.hhi < 0.1 ? 'Moderate' : 'Concentrated'}
        />
        <StatCard
          label="Gini Coefficient"
          value={stats.gini.toFixed(4)}
          subValue={stats.gini < 0.5 ? 'Equal' : stats.gini < 0.8 ? 'Moderate' : 'Unequal'}
        />
        <StatCard
          label="Whales"
          value={holder_breakdowns.categories.whale.toLocaleString()}
        />
        <StatCard
          label="Supply"
          value={formatNumber(parseInt(token.supply) / Math.pow(10, token.decimals))}
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
            value={`$${formatNumber(pnl.realized_pnl_total)}`}
            trend={pnl.realized_pnl_total >= 0 ? 'up' : 'down'}
          />
          <StatCard
            label="Total Unrealized PnL"
            value={`$${formatNumber(pnl.unrealized_pnl_total)}`}
            trend={pnl.unrealized_pnl_total >= 0 ? 'up' : 'down'}
          />
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <HolderDeltasChart deltas={holder_deltas} />
        <HolderDistributionChart categories={holder_breakdowns.categories} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ValueBreakdownChart breakdowns={holder_breakdowns} />
        {holders && (
          <TopHoldersTable
            holders={holders.holders}
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
                tokenTicker={token.ticker}
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
