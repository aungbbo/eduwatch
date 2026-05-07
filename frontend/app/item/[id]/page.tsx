"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { addWatchlist, fetchItem, getInsight } from "@/lib/api";
import { ItemDetail } from "@/types";

export default function ItemDetailPage() {
  const params = useParams<{ id: string }>();
  const itemId = Number(params.id);

  const [item, setItem] = useState<ItemDetail | null>(null);
  const [targetPrice, setTargetPrice] = useState("");
  const [insight, setInsight] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await fetchItem(itemId);
        setItem(data);
      } catch (err) {
        setError("Could not load item details.");
      } finally {
        setLoading(false);
      }
    };
    if (!Number.isNaN(itemId)) {
      load();
    }
  }, [itemId]);

  // Aggregate: one data point per day using the lowest price across all stores
  const dailyPrices = useMemo(() => {
    if (!item) return [];
    const byDate = new Map<string, number>();
    for (const p of item.price_history) {
      const d = new Date(p.captured_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
      const existing = byDate.get(d);
      if (existing === undefined || p.price < existing) {
        byDate.set(d, p.price);
      }
    }
    return Array.from(byDate.entries())
      .sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
      .map(([date, price]) => ({ date, price }));
  }, [item]);

  const chartData = useMemo(() => {
    // Deduplicate consecutive identical prices for a clean step chart
    const deduped: { date: string; price: number }[] = [];
    for (const point of dailyPrices) {
      if (deduped.length === 0 || deduped[deduped.length - 1].price !== point.price) {
        deduped.push(point);
      }
    }
    return deduped;
  }, [dailyPrices]);

  const priceStats = useMemo(() => {
    if (dailyPrices.length === 0) return null;
    const prices = dailyPrices.map((p) => p.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const latest = prices[prices.length - 1];
    const delta = latest - prices[0];
    return { min, max, latest, delta };
  }, [dailyPrices]);

  const onAddWatchlist = async (e: FormEvent) => {
    e.preventDefault();
    if (!targetPrice) return;
    await addWatchlist({
      user_tag: "demo-student",
      item_id: itemId,
      target_price: Number(targetPrice)
    });
    setMessage("Added to watchlist for demo-student.");
    setTargetPrice("");
  };

  const onGenerateInsight = async () => {
    const data = await getInsight(itemId);
    setInsight(data.recommendation);
  };

  if (loading) return <main className="p-6 text-slate-700">Loading item...</main>;
  if (error || !item) return <main className="p-6 text-rose-700">{error || "Item not found."}</main>;

  return (
    <main className="mx-auto max-w-6xl p-6 md:p-8">
      <Link href="/" className="text-sm font-medium text-indigo-700 hover:text-indigo-800">
        ← Back to dashboard
      </Link>

      <section className="mt-4 rounded-3xl border border-sky-100 bg-white p-6 shadow-sm">
        <p className="inline-flex rounded-full bg-sky-50 px-2 py-1 text-xs font-medium text-sky-700">{item.category}</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-900">{item.name}</h1>
        <p className="mt-2 text-slate-600">{item.description}</p>
        <p className="mt-4 inline-flex rounded-xl bg-emerald-50 px-3 py-2 font-semibold text-emerald-700">
          Current price: {priceStats ? `$${priceStats.latest.toFixed(2)}` : "N/A"}
        </p>
        {priceStats && (
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Lowest recorded</p>
              <p className="mt-1 font-semibold text-emerald-700">${priceStats.min.toFixed(2)}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Highest recorded</p>
              <p className="mt-1 font-semibold text-rose-700">${priceStats.max.toFixed(2)}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Trend</p>
              <p className={`mt-1 font-semibold ${priceStats.delta <= 0 ? "text-emerald-700" : "text-amber-700"}`}>
                {priceStats.delta <= 0 ? "Dropping" : "Rising"} ({priceStats.delta.toFixed(2)})
              </p>
            </div>
          </div>
        )}
      </section>

      <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Price history</h2>
        <p className="mt-1 text-sm text-slate-600">Lowest price across all stores, each point marks a price change.</p>
        <div className="mt-4 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis
                dataKey="date"
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
                tickFormatter={(value: string) =>
                  new Date(value).toLocaleDateString("en-US", { month: "short", year: "numeric" })
                }
              />
              <YAxis
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => `$${v}`}
                width={64}
                domain={["auto", "auto"]}
              />
              <Tooltip
                formatter={(value: number) => [`$${value.toFixed(2)}`, "Best price"]}
                labelFormatter={(label: string) =>
                  new Date(label).toLocaleDateString("en-US", {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })
                }
                contentStyle={{
                  borderRadius: "0.75rem",
                  borderColor: "#e2e8f0",
                  fontSize: "13px",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.07)",
                }}
                labelStyle={{ color: "#475569", fontWeight: 500 }}
              />
              <Line
                type="stepAfter"
                dataKey="price"
                stroke="#4338ca"
                strokeWidth={1.5}
                dot={{ r: 3, fill: "#4338ca", strokeWidth: 0 }}
                activeDot={{ r: 5, fill: "#4338ca", strokeWidth: 0 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-2">
        <form onSubmit={onAddWatchlist} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">Target price</h3>
          <p className="mt-1 text-sm text-slate-600">Save this item at your ideal price.</p>
          <input
            type="number"
            min="1"
            step="0.01"
            className="mt-3 w-full rounded-xl border border-slate-200 px-3 py-2 outline-none ring-sky-200 transition focus:ring-2"
            placeholder="e.g. 49.99"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
          />
          <button
            type="submit"
            className="mt-3 rounded-xl bg-indigo-600 px-3 py-2 font-medium text-white transition hover:bg-indigo-700"
          >
            Save target
          </button>
          {message && <p className="mt-2 text-sm font-medium text-emerald-700">{message}</p>}
        </form>

        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">AI recommendation</h3>
          <p className="mt-1 text-sm text-slate-600">A quick buy-now or wait suggestion.</p>
          <button
            onClick={onGenerateInsight}
            className="mt-3 rounded-xl bg-sky-600 px-3 py-2 font-medium text-white transition hover:bg-sky-700"
            type="button"
          >
            Generate
          </button>
          <p className="mt-3 rounded-lg bg-slate-50 p-3 text-slate-700">
            {insight || "No recommendation yet."}
          </p>
        </div>
      </section>
    </main>
  );
}
