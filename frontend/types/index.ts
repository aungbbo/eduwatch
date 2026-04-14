export type Item = {
  id: number;
  name: string;
  category: string;
  description?: string;
  lowest_price?: number | null;
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
