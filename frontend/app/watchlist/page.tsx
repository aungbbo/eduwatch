"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchItem, getWatchlist } from "@/lib/api";
import { ItemDetail, WatchlistEntry } from "@/types";

const USER_TAG = "demo-student";
const formatCurrency = (value?: number | null) =>
  typeof value === "number" ? `$${value.toFixed(2)}` : "N/A";

type EnrichedEntry = WatchlistEntry & {
  item?: ItemDetail;
};

export default function WatchlistPage() {
  const [entries, setEntries] = useState<EnrichedEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const watchlist = await getWatchlist(USER_TAG);
        const enriched = await Promise.all(
          watchlist.map(async (entry) => {
            try {
              const item = await fetchItem(entry.item_id);
              return { ...entry, item };
            } catch {
              return { ...entry };
            }
          })
        );
        setEntries(enriched);
      } catch {
        setError("Could not load watchlist. Is backend running?");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const getLatestPrice = (item?: ItemDetail): number | null => {
    if (!item || item.price_history.length === 0) return null;
    const byDate = new Map<string, number>();
    for (const p of item.price_history) {
      const d = new Date(p.captured_at).toISOString().slice(0, 10);
      const existing = byDate.get(d);
      if (existing === undefined || p.price < existing) byDate.set(d, p.price);
    }
    const sorted = Array.from(byDate.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    return sorted[sorted.length - 1]?.[1] ?? null;
  };

  return (
    <main className="mx-auto max-w-4xl p-6 md:p-8">
      <Link href="/" className="text-sm font-medium text-indigo-700 hover:text-indigo-800">
        ← Back to dashboard
      </Link>

      <section className="mt-4 rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-700 via-blue-700 to-sky-600 p-6 text-white shadow-lg">
        <h1 className="text-2xl font-bold md:text-3xl">My Watchlist</h1>
        <p className="mt-1 text-sky-100 text-sm">Tracking {entries.length} item{entries.length !== 1 ? "s" : ""} for {USER_TAG}.</p>
      </section>

      {loading && <p className="mt-6 rounded-lg bg-white p-4 text-slate-700">Loading watchlist...</p>}
      {error && <p className="mt-6 rounded-lg bg-rose-50 p-4 text-rose-700">{error}</p>}

      {!loading && !error && entries.length === 0 && (
        <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
          <p className="text-slate-500">No items in your watchlist yet.</p>
          <Link href="/" className="mt-3 inline-block text-sm font-medium text-indigo-700 hover:text-indigo-800">
            Browse items →
          </Link>
        </div>
      )}

      {!loading && !error && entries.length > 0 && (
        <section className="mt-6 flex flex-col gap-3">
          {entries.map((entry) => {
            const currentPrice = getLatestPrice(entry.item);
            const met = currentPrice !== null && currentPrice <= entry.target_price;
            return (
              <div
                key={entry.id}
                className={`rounded-2xl border bg-white p-5 shadow-sm ${met ? "border-emerald-300" : "border-slate-200"}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <Link
                      href={`/item/${entry.item_id}`}
                      className="text-lg font-semibold text-slate-900 hover:text-indigo-700"
                    >
                      {entry.item?.name ?? `Item #${entry.item_id}`}
                    </Link>
                    <p className="mt-0.5 text-sm text-slate-500">
                      Added {new Date(entry.created_at).toLocaleDateString("en-US", {
                        month: "short", day: "numeric", year: "numeric",
                      })}
                    </p>
                  </div>
                  {met && (
                    <span className="flex-shrink-0 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                      Target reached
                    </span>
                  )}
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
                  <div className="rounded-xl bg-slate-50 p-3">
                    <p className="text-xs text-slate-500">Current price</p>
                    <p className="mt-1 font-semibold text-slate-800">{formatCurrency(currentPrice)}</p>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-3">
                    <p className="text-xs text-slate-500">Your target</p>
                    <p className="mt-1 font-semibold text-indigo-700">{formatCurrency(entry.target_price)}</p>
                  </div>
                  {currentPrice !== null && (
                    <div className="rounded-xl bg-slate-50 p-3">
                      <p className="text-xs text-slate-500">Difference</p>
                      <p className={`mt-1 font-semibold ${met ? "text-emerald-700" : "text-rose-600"}`}>
                        {met ? "−" : "+"}{formatCurrency(Math.abs(currentPrice - entry.target_price))}
                      </p>
                    </div>
                  )}
                </div>

                <Link
                  href={`/item/${entry.item_id}`}
                  className="mt-3 inline-block text-sm font-medium text-indigo-700 hover:text-indigo-800"
                >
                  View price history →
                </Link>
              </div>
            );
          })}
        </section>
      )}
    </main>
  );
}
