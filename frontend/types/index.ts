export type Item = {
  id: number;
  name: string;
  category: string;
  description?: string;
  lowest_price?: number | null;
  current_price?: number | null;
};

export type PriceSnapshot = {
  id: number;
  store: string;
  price: number;
  currency: string;
  in_stock: boolean;
  captured_at: string;
};

export type ItemDetail = Item & {
  price_history: PriceSnapshot[];
};

export type WatchlistEntry = {
  id: number;
  user_tag: string;
  item_id: number;
  target_price: number;
  created_at: string;
};

export type Advice = {
  action: "BUY" | "WAIT";
  confidence: number;
  reason: string;
  signals: string[];
};

export type PriceStatistics = {
  current: number;
  all_time_low: number;
  all_time_high: number;
  avg_30d: number;
  avg_90d: number;
  avg_365d: number;
  std_30d: number;
  pct_vs_30d_avg: number;
  pct_vs_90d_avg: number | null;
  trend_7d: number | null;
  trend_30d: number | null;
};

export type Insight = {
  item_id: number;
  current_price: number;
  predicted_price: number;
  advice: Advice;
  statistics: PriceStatistics;
  feature_importance: Record<string, number>;
  data_points: number;
};
