import type { WalletStats } from '../types';

interface WalletAnalysisCardProps {
  stats: WalletStats;
  walletAddress: string;
  tokenTicker: string;
}

export function WalletAnalysisCard({ stats, walletAddress, tokenTicker }: WalletAnalysisCardProps) {
  const formatPnL = (value: number) => {
    const prefix = value >= 0 ? '+' : '';
    return `${prefix}$${Math.abs(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  };

  const formatTime = (seconds: number | null) => {
    if (seconds === null) return 'N/A';
    const days = Math.floor(seconds / 86400);
    if (days > 365) {
      const years = (days / 365).toFixed(1);
      return `${years} years`;
    }
    if (days > 30) {
      const months = (days / 30).toFixed(1);
      return `${months} months`;
    }
    return `${days} days`;
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      whale: 'text-purple-400',
      dolphin: 'text-blue-400',
      fish: 'text-cyan-400',
      crab: 'text-green-400',
      shrimp: 'text-yellow-400',
    };
    return colors[category.toLowerCase()] || 'text-gray-400';
  };

  const truncateAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-6)}`;
  };

  const holdingData = [
    { name: 'Diamond', value: stats.holding_breakdown.diamond, color: 'bg-cyan-400' },
    { name: 'Gold', value: stats.holding_breakdown.gold, color: 'bg-yellow-400' },
    { name: 'Silver', value: stats.holding_breakdown.silver, color: 'bg-gray-300' },
    { name: 'Bronze', value: stats.holding_breakdown.bronze, color: 'bg-orange-400' },
    { name: 'Wood', value: stats.holding_breakdown.wood, color: 'bg-amber-600' },
  ];

  const total = holdingData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold">Wallet Analysis</h3>
          <p className="font-mono text-sm text-gray-400">{truncateAddress(walletAddress)}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getCategoryColor(stats.holder_category)} bg-gray-700/50`}>
          {stats.holder_category}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <span className="text-sm text-gray-400">Holdings</span>
          <p className="text-xl font-bold">
            {stats.amount.toLocaleString()} {tokenTicker}
          </p>
        </div>
        <div>
          <span className="text-sm text-gray-400">Avg Time Held</span>
          <p className="text-xl font-bold">{formatTime(stats.avg_time_held)}</p>
        </div>
        <div>
          <span className="text-sm text-gray-400">Unrealized PnL</span>
          <p className={`text-xl font-bold ${stats.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatPnL(stats.unrealized_pnl)}
          </p>
        </div>
        <div>
          <span className="text-sm text-gray-400">Realized PnL</span>
          <p className={`text-xl font-bold ${stats.realized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatPnL(stats.realized_pnl)}
          </p>
        </div>
      </div>

      <div>
        <h4 className="text-sm text-gray-400 mb-2">Holding Breakdown (by age)</h4>
        <div className="h-4 flex rounded-full overflow-hidden bg-gray-700">
          {holdingData.map((item) => (
            item.value > 0 && (
              <div
                key={item.name}
                className={`${item.color} h-full`}
                style={{ width: `${(item.value / total) * 100}%` }}
                title={`${item.name}: ${item.value.toLocaleString()}`}
              />
            )
          ))}
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-400">
          {holdingData.map((item) => (
            <span key={item.name}>{item.name}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
