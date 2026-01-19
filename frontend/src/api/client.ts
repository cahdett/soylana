import axios from 'axios';
import type {
  Token,
  TokenAnalysis,
  HolderList,
  HolderDeltas,
  HolderBreakdowns,
  WalletStats,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Token endpoints
export async function listTokens(limit = 50, offset = 0): Promise<{ total: number; tokens: Token[] }> {
  const { data } = await api.get('/tokens', { params: { limit, offset } });
  return data;
}

export async function getToken(address: string): Promise<Token> {
  const { data } = await api.get(`/tokens/${address}`);
  return data;
}

export async function getTokenAnalysis(address: string): Promise<TokenAnalysis> {
  const { data } = await api.get(`/tokens/${address}/analysis`);
  return data;
}

// Holder endpoints
export async function getHolders(
  tokenAddress: string,
  options?: {
    minAmount?: number;
    maxAmount?: number;
    limit?: number;
    offset?: number;
  }
): Promise<HolderList> {
  const { data } = await api.get(`/tokens/${tokenAddress}/holders`, {
    params: options,
  });
  return data;
}

export async function getHolderDeltas(tokenAddress: string): Promise<HolderDeltas> {
  const { data } = await api.get(`/tokens/${tokenAddress}/holders/deltas`);
  return data;
}

export async function getHolderBreakdowns(tokenAddress: string): Promise<HolderBreakdowns> {
  const { data } = await api.get(`/tokens/${tokenAddress}/holders/breakdowns`);
  return data;
}

// Wallet analysis
export async function getWalletStats(
  tokenAddress: string,
  walletAddress: string
): Promise<WalletStats> {
  const { data } = await api.get(`/tokens/${tokenAddress}/wallet/${walletAddress}`);
  return data;
}

// Cross-checker
export interface CrossCheckerResult {
  common_wallets: {
    wallet_address: string;
    holdings: Record<string, {
      token_name: string;
      raw_amount: number;
      adjusted_amount: number;
      rank: number;
    }>;
    tokens_held: number;
  }[];
  tokens: {
    address: string;
    name: string;
    decimals: number;
    holders_fetched: number;
  }[];
  total_common: number;
  query: {
    token_count: number;
    max_holders_per_token: number;
    min_usd_value: number | null;
  };
}

export async function crossCheckWallets(
  tokenAddresses: string[],
  options?: {
    minUsdValue?: number;
    maxHoldersPerToken?: number;
  }
): Promise<CrossCheckerResult> {
  const { data } = await api.post('/cross-checker', {
    token_addresses: tokenAddresses,
    min_usd_value: options?.minUsdValue,
    max_holders_per_token: options?.maxHoldersPerToken ?? 1000,
  }, {
    timeout: 120000, // 2 minute timeout for this heavy operation
  });
  return data;
}

// Health check
export async function healthCheck(): Promise<{ status: string }> {
  const { data } = await api.get('/health');
  return data;
}
