import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { crossCheckWallets, type CrossCheckerResult } from '../api/client';

export function CrossChecker() {
  const navigate = useNavigate();
  const [tokenInput, setTokenInput] = useState('');
  const [maxHolders, setMaxHolders] = useState(1000);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CrossCheckerResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    // Parse token addresses (split by newlines, commas, or spaces)
    const addresses = tokenInput
      .split(/[\n,\s]+/)
      .map(addr => addr.trim())
      .filter(addr => addr.length > 0);

    if (addresses.length < 2) {
      setError('Please enter at least 2 token addresses');
      return;
    }

    if (addresses.length > 10) {
      setError('Maximum 10 tokens allowed per cross-check');
      return;
    }

    setIsLoading(true);

    try {
      const data = await crossCheckWallets(addresses, {
        maxHoldersPerToken: maxHolders,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cross-check wallets');
    } finally {
      setIsLoading(false);
    }
  };

  const formatAmount = (amount: number) => {
    if (amount >= 1_000_000_000) return `${(amount / 1_000_000_000).toFixed(2)}B`;
    if (amount >= 1_000_000) return `${(amount / 1_000_000).toFixed(2)}M`;
    if (amount >= 1_000) return `${(amount / 1_000).toFixed(2)}K`;
    return amount.toFixed(2);
  };

  const truncateAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="text-gray-400 hover:text-white mb-4 flex items-center gap-2"
        >
          ← Back to Home
        </button>
        <h1 className="text-3xl font-bold mb-2">Wallet Cross-Checker</h1>
        <p className="text-gray-400">
          Find wallets that hold ALL of the tokens you specify. Great for finding smart money or insider wallets.
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 mb-6 max-w-2xl">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Token Addresses (2-10 tokens)
            </label>
            <textarea
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              placeholder="Paste token addresses here, one per line or separated by commas..."
              className="w-full h-40 px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter Solana token contract addresses, one per line or comma-separated
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Max Holders to Check Per Token
            </label>
            <select
              value={maxHolders}
              onChange={(e) => setMaxHolders(Number(e.target.value))}
              className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
            >
              <option value={100}>100 (Fast)</option>
              <option value={500}>500 (Balanced)</option>
              <option value={1000}>1,000 (Default)</option>
              <option value={2000}>2,000 (Thorough)</option>
              <option value={5000}>5,000 (Very Thorough - Slow)</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Higher values find more wallets but take longer
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded-lg text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Scanning... This may take a minute
              </span>
            ) : (
              'Find Common Wallets'
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div>
          {/* Summary */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Results Summary</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-400">Tokens Analyzed</p>
                <p className="text-2xl font-bold">{result.tokens.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Common Wallets Found</p>
                <p className="text-2xl font-bold text-purple-400">{result.total_common}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Max Holders Checked</p>
                <p className="text-2xl font-bold">{result.query.max_holders_per_token}</p>
              </div>
            </div>

            {/* Token list */}
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">Tokens in query:</p>
              <div className="flex flex-wrap gap-2">
                {result.tokens.map((token) => (
                  <span
                    key={token.address}
                    className="px-3 py-1 bg-gray-700 rounded-full text-sm"
                    title={token.address}
                  >
                    {token.name} ({token.holders_fetched} holders)
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Common Wallets Table */}
          {result.total_common > 0 ? (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h2 className="text-xl font-bold mb-4">
                Common Wallets ({result.total_common})
              </h2>
              <p className="text-sm text-gray-400 mb-4">
                These wallets hold ALL {result.tokens.length} tokens. Sorted by average holder rank (top holders first).
              </p>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-gray-700">
                      <th className="pb-3 font-medium">#</th>
                      <th className="pb-3 font-medium">Wallet</th>
                      {result.tokens.map((token) => (
                        <th key={token.address} className="pb-3 font-medium text-right">
                          {token.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.common_wallets.slice(0, 100).map((wallet, idx) => (
                      <tr
                        key={wallet.wallet_address}
                        className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
                      >
                        <td className="py-3 text-gray-400">{idx + 1}</td>
                        <td className="py-3">
                          <a
                            href={`https://solscan.io/account/${wallet.wallet_address}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-mono text-purple-400 hover:text-purple-300 transition-colors"
                          >
                            {truncateAddress(wallet.wallet_address)}
                          </a>
                        </td>
                        {result.tokens.map((token) => {
                          const holding = wallet.holdings[token.address];
                          return (
                            <td key={token.address} className="py-3 text-right">
                              <div className="font-medium">
                                {formatAmount(holding?.adjusted_amount ?? 0)}
                              </div>
                              <div className="text-xs text-gray-500">
                                Rank #{holding?.rank ?? '-'}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>

                {result.total_common > 100 && (
                  <p className="text-sm text-gray-400 mt-4 text-center">
                    Showing top 100 of {result.total_common} wallets
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 text-center">
              <p className="text-xl text-gray-400">No common wallets found</p>
              <p className="text-sm text-gray-500 mt-2">
                Try increasing the "Max Holders to Check" value or using different tokens
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
