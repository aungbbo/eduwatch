"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

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

  const chartData = useMemo(() => {
    if (!item) return [];
    return item.price_history.map((p) => ({
      date: new Date(p.captured_at).toLocaleDateString(),
      price: p.price
    }));
  }, [item]);

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

  if (loading) return <main className="p-6">Loading...</main>;
  if (error || !item) return <main className="p-6 text-red-600">{error || "Item not found."}</main>;

  return (
    <main className="mx-auto max-w-5xl p-6">
      <Link href="/" className="text-sm text-slate-600">
        ← Back to dashboard
      </Link>

      <h1 className="mt-4 text-3xl font-bold">{item.name}</h1>
      <p className="mt-2 text-slate-600">{item.description}</p>
      <p className="mt-3 font-medium text-emerald-700">
        Current Best: {item.lowest_price ? `$${item.lowest_price.toFixed(2)}` : "N/A"}
      </p>

      <section className="mt-6 rounded border bg-white p-4">
        <h2 className="text-lg font-semibold">Price Trend</h2>
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="price" stroke="#0f172a" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-2">
        <form onSubmit={onAddWatchlist} className="rounded border bg-white p-4">
          <h3 className="font-semibold">Set Target Price</h3>
          <input
            type="number"
            min="1"
            step="0.01"
            className="mt-3 w-full rounded border px-3 py-2"
            placeholder="e.g. 49.99"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
          />
          <button type="submit" className="mt-3 rounded bg-slate-900 px-3 py-2 text-white">
            Add to Watchlist
          </button>
          {message && <p className="mt-2 text-sm text-emerald-700">{message}</p>}
        </form>

        <div className="rounded border bg-white p-4">
          <h3 className="font-semibold">AI Buy Tip</h3>
          <button
            onClick={onGenerateInsight}
            className="mt-3 rounded bg-indigo-600 px-3 py-2 text-white"
            type="button"
          >
            Generate Insight
          </button>
          <p className="mt-3 text-slate-700">
            {insight || "No insight yet. Click the button to generate recommendation."}
          </p>
        </div>
      </section>
    </main>
  );
}
