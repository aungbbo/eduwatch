import { Item, ItemDetail, WatchlistEntry } from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export async function fetchItems(params: {
  search?: string;
  category?: string;
  maxPrice?: number;
}): Promise<Item[]> {
  const query = new URLSearchParams();
  if (params.search) query.set("search", params.search);
  if (params.category && params.category !== "all")
    query.set("category", params.category);
  if (params.maxPrice) query.set("max_price", String(params.maxPrice));

  const res = await fetch(`${API_BASE}/items?${query.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch items");
  return res.json();
}

export async function fetchItem(itemId: number): Promise<ItemDetail> {
  const res = await fetch(`${API_BASE}/items/${itemId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch item details");
  return res.json();
}

export async function addWatchlist(payload: {
  user_tag: string;
  item_id: number;
  target_price: number;
}): Promise<WatchlistEntry> {
  const res = await fetch(`${API_BASE}/watchlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to add watchlist");
  return res.json();
}

export async function getInsight(itemId: number): Promise<{ recommendation: string }> {
  const res = await fetch(`${API_BASE}/insights/${itemId}`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to fetch insight");
  return res.json();
}
