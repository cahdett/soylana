import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { crossCheckWallets, type CrossCheckerResult, type TokenInput } from '../api/client';

interface TokenEntry {
  id: string;
  address: string;
  fromDate: string;
  toDate: string;
}

function generateId() {
  return Math.random().toString(36).substring(2, 9);
}

export function CrossChecker() {
  const navigate = useNavigate();
  const [tokens, setTokens] = useState<TokenEntry[]>([
    { id: generateId(), address: '', fromDate: '', toDate: '' },
    { id: generateId(), address: '', fromDate: '', toDate: '' },
  ]);
  const [maxPages, setMaxPages] = useState(50);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CrossCheckerResult | null>(null);

  const addToken = () => {
    if (tokens.length < 10) {
      setTokens([...tokens, { id: generateId(), address: '', fromDate: '', toDate: '' }]);
    }
  };

  const removeToken = (id: string) => {
    if (tokens.length > 2) {
      setTokens(tokens.filter(t => t.id !== id));
    }
  };

  const updateToken = (id: string, field: keyof TokenEntry, value: string) => {
    setTokens(tokens.map(t => t.id === id ? { ...t, [field]: value } : t));
  };

  const dateToUnix = (dateStr: string): number | undefined => {
    if (!dateStr) return undefined;
    return Math.floor(new Date(dateStr).getTime() / 1000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    // Filter tokens with valid addresses
    const validTokens = tokens.filter(t => t.address.trim().length > 0);

    if (validTokens.length < 2) {
      setError('Please enter at least 2 token addresses');
      return;
    }

    // Build token inputs
    const tokenInputs: TokenInput[] = validTokens.map(t => ({
      address: t.address.trim(),
      from_time: dateToUnix(t.fromDate),
      to_time: dateToUnix(t.toDate),
    }));

    setIsLoading(true);

    try {
      const data = await crossCheckWallets(tokenInputs, {
        maxPagesPerToken: maxPages,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cross-check wallets');
    } finally {
      setIsLoading(false);
    }
  };

  const truncateAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatDateTime = (timestamp: number | null): string => {
    if (!timestamp) return 'All time';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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
          Find wallets that have <strong>traded</strong> ALL of the specified tokens.
          Set timeframes per token to narrow down the search.
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 mb-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <div className="flex justify-between items-center mb-3">
              <label className="block text-sm font-medium text-gray-300">
                Tokens to Cross-Check (2-10)
              </label>
              <button
                type="button"
                onClick={addToken}
                disabled={tokens.length >= 10}
                className="text-sm px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded transition-colors"
              >
                + Add Token
              </button>
            </div>

            <div className="space-y-3">
              {tokens.map((token, index) => (
                <div key={token.id} className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-start gap-3">
                    <span className="text-gray-500 mt-2 w-6">{index + 1}.</span>

                    <div className="flex-1 space-y-3">
                      {/* Token Address */}
                      <div>
                        <input
                          type="text"
                          value={token.address}
                          onChange={(e) => updateToken(token.id, 'address', e.target.value)}
                          placeholder="Token address (e.g., So11111111111111111111111111111111111111112)"
                          className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 font-mono text-sm"
                        />
                      </div>

                      {/* DateTime Range */}
                      <div className="flex flex-wrap gap-3">
                        <div className="flex items-center gap-2">
                          <label className="text-sm text-gray-400 whitespace-nowrap">From:</label>
                          <input
                            type="datetime-local"
                            value={token.fromDate}
                            onChange={(e) => updateToken(token.id, 'fromDate', e.target.value)}
                            className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-purple-500"
                          />
                        </div>
                        <div className="flex items-center gap-2">
                          <label className="text-sm text-gray-400 whitespace-nowrap">To:</label>
                          <input
                            type="datetime-local"
                            value={token.toDate}
                            onChange={(e) => updateToken(token.id, 'toDate', e.target.value)}
                            className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-purple-500"
                          />
                        </div>
                        <span className="text-xs text-gray-500 self-center">(Leave blank for all time)</span>
                      </div>
                    </div>

                    {/* Remove Button */}
                    {tokens.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeToken(token.id)}
                        className="text-red-400 hover:text-red-300 p-1"
                        title="Remove token"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Max Transfer Pages Per Token
            </label>
            <select
              value={maxPages}
              onChange={(e) => setMaxPages(Number(e.target.value))}
              className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
            >
              <option value={10}>10 pages (~1,000 transfers) - Fast</option>
              <option value={25}>25 pages (~2,500 transfers) - Quick</option>
              <option value={50}>50 pages (~5,000 transfers) - Default</option>
              <option value={100}>100 pages (~10,000 transfers) - Thorough</option>
              <option value={200}>200 pages (~20,000 transfers) - Very Thorough</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Higher values scan more historical transfers but take longer
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
                Scanning transfers... This may take a few minutes
              </span>
            ) : (
              'Find Common Traders'
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
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-400">Tokens Analyzed</p>
                <p className="text-2xl font-bold">{result.tokens.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Common Traders Found</p>
                <p className="text-2xl font-bold text-purple-400">{result.total_common}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Max Pages Scanned</p>
                <p className="text-2xl font-bold">{result.query.max_pages_per_token}</p>
              </div>
            </div>

            {/* Token list with timeframes */}
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">Tokens scanned:</p>
              <div className="space-y-2">
                {result.tokens.map((token) => (
                  <div
                    key={token.address}
                    className="flex items-center justify-between px-3 py-2 bg-gray-700 rounded-lg text-sm"
                  >
                    <span className="font-medium">{token.name}</span>
                    <div className="flex items-center gap-4 text-gray-400">
                      <span>{token.traders_found.toLocaleString()} traders</span>
                      <span>
                        {formatDateTime(token.from_time)} - {formatDateTime(token.to_time)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Common Wallets Table */}
          {result.total_common > 0 ? (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h2 className="text-xl font-bold mb-4">
                Common Traders ({result.total_common})
              </h2>
              <p className="text-sm text-gray-400 mb-4">
                These wallets have traded ALL {result.tokens.length} tokens within the specified timeframes.
              </p>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-gray-700">
                      <th className="pb-3 font-medium">#</th>
                      <th className="pb-3 font-medium">Wallet Address</th>
                      <th className="pb-3 font-medium text-center">Tokens Traded</th>
                      <th className="pb-3 font-medium text-right">Actions</th>
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
                        <td className="py-3 text-center">
                          <div className="flex flex-wrap gap-1 justify-center">
                            {result.tokens.map((token) => (
                              <span
                                key={token.address}
                                className="px-2 py-0.5 bg-green-600/30 text-green-400 rounded text-xs"
                                title={token.address}
                              >
                                {token.name}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 text-right">
                          <a
                            href={`https://solscan.io/account/${wallet.wallet_address}#transfers`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-gray-400 hover:text-white transition-colors"
                          >
                            View Transfers →
                          </a>
                        </td>
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
              <p className="text-xl text-gray-400">No common traders found</p>
              <p className="text-sm text-gray-500 mt-2">
                Try increasing the "Max Transfer Pages" value, adjusting timeframes, or using different tokens
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
