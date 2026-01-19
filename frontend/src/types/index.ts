// Token types
export interface Token {
  address: string;
  name: string;
  ticker: string;
  symbol?: string;
  network: string;
  decimals: number;
  supply: string | number;
  total_supply?: string | number;
}

export interface TokenStats {
  hhi: number;
  gini: number;
  median_holder_position: number;
  avg_time_held: number | null;
  retention_rate: number | null;
}

export interface TokenPnL {
  break_even_price: number | null;
  realized_pnl_total: number;
  unrealized_pnl_total: number;
}

export interface WalletCategories {
  diamond: number;
  gold: number;
  silver: number;
  bronze: number;
  wood: number;
  new_holders: number;
}

export interface SupplyBreakdown {
  diamond: number;
  gold: number;
  silver: number;
  bronze: number;
  wood: number;
}

// Holder types
export interface Holder {
  address: string;
  spl_token_account: string | null;
  amount: number;
  rank: number;
}

export interface HolderList {
  holder_count: number;
  total: number;
  holders: Holder[];
}

export interface HolderDeltas {
  hour_1: number;
  hours_2: number;
  hours_4: number;
  hours_12: number;
  day_1: number;
  days_3: number;
  days_7: number;
  days_14: number;
  days_30: number;
}

export interface HolderCategories {
  shrimp: number;
  crab: number;
  fish: number;
  dolphin: number;
  whale: number;
}

export interface HolderBreakdowns {
  total_holders: number;
  holders_over_10_usd: number;
  holders_over_100_usd: number;
  holders_over_1000_usd: number;
  holders_over_10000_usd: number;
  holders_over_100k_usd: number;
  holders_over_1m_usd: number;
  categories: HolderCategories;
}

export interface HoldingBreakdown {
  diamond: number;
  gold: number;
  silver: number;
  bronze: number;
  wood: number;
}

export interface WalletStats {
  amount: number;
  holder_category: string;
  avg_time_held: number | null;
  holding_breakdown: HoldingBreakdown;
  unrealized_pnl: number;
  realized_pnl: number;
}

// Combined analysis
export interface TokenAnalysis {
  token: Token;
  stats: TokenStats;
  holder_deltas: HolderDeltas;
  holder_breakdowns: HolderBreakdowns;
  pnl: TokenPnL | null;
  wallet_categories: WalletCategories | null;
  supply_breakdown: SupplyBreakdown | null;
}
