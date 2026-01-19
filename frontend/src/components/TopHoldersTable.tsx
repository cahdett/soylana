import type { Holder } from '../types';

interface TopHoldersTableProps {
  holders: Holder[];
  totalSupply?: number;
  decimals?: number;
  onWalletClick?: (address: string) => void;
}

export function TopHoldersTable({
  holders,
  totalSupply = 0,
  decimals = 0,
  onWalletClick
}: TopHoldersTableProps) {
  const formatAmount = (amount: number) => {
    if (amount >= 1_000_000_000) {
      return `${(amount / 1_000_000_000).toFixed(2)}B`;
    }
    if (amount >= 1_000_000) {
      return `${(amount / 1_000_000).toFixed(2)}M`;
    }
    if (amount >= 1_000) {
      return `${(amount / 1_000).toFixed(2)}K`;
    }
    return amount.toFixed(2);
  };

  const truncateAddress = (address: string) => {
    return `${address.slice(0, 4)}...${address.slice(-4)}`;
  };

  // Adjust raw amount by decimals
  const adjustAmount = (rawAmount: number) => {
    if (decimals === 0) return rawAmount;
    return rawAmount / Math.pow(10, decimals);
  };

  // Calculate percentage of total supply
  const calculatePercentage = (rawAmount: number) => {
    if (totalSupply === 0) return 0;
    return (rawAmount / totalSupply) * 100;
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Top Holders</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="pb-3 font-medium">Rank</th>
              <th className="pb-3 font-medium">Address</th>
              <th className="pb-3 font-medium text-right">Amount</th>
              <th className="pb-3 font-medium text-right">% Supply</th>
            </tr>
          </thead>
          <tbody>
            {holders.map((holder) => {
              const adjustedAmount = adjustAmount(holder.amount ?? 0);
              const percentage = calculatePercentage(holder.amount ?? 0);

              return (
                <tr
                  key={holder.address}
                  className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
                >
                  <td className="py-3 text-gray-400">#{holder.rank}</td>
                  <td className="py-3">
                    <button
                      onClick={() => onWalletClick?.(holder.address)}
                      className="font-mono text-purple-400 hover:text-purple-300 transition-colors"
                    >
                      {truncateAddress(holder.address)}
                    </button>
                  </td>
                  <td className="py-3 text-right font-medium">
                    {formatAmount(adjustedAmount)}
                  </td>
                  <td className="py-3 text-right text-gray-400">
                    {percentage.toFixed(2)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
