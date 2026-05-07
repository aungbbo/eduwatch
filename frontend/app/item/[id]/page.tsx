"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { addWatchlist, fetchItem, sendChat } from "@/lib/api";
import { ItemDetail } from "@/types";

type ChatMessage = { role: "user" | "assistant"; content: string };

export default function ItemDetailPage() {
  const params = useParams<{ id: string }>();
  const itemId = Number(params.id);

  const [item, setItem] = useState<ItemDetail | null>(null);
  const [targetPrice, setTargetPrice] = useState("");
  const [watchlistMsg, setWatchlistMsg] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Chat state
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await fetchItem(itemId);
        setItem(data);
      } catch {
        setError("Could not load item details.");
      } finally {
        setLoading(false);
      }
    };
    if (!Number.isNaN(itemId)) load();
  }, [itemId]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

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
      target_price: Number(targetPrice),
    });
    setWatchlistMsg("Added to watchlist.");
    setTargetPrice("");
  };

  const onSendChat = async () => {
    const text = chatInput.trim();
    if (!text || chatLoading) return;
    setChatInput("");
    const userMsg: ChatMessage = { role: "user", content: text };
    const newHistory = [...chatHistory, userMsg];
    setChatHistory(newHistory);
    setChatLoading(true);
    try {
      const { reply } = await sendChat(itemId, text, chatHistory);
      setChatHistory([...newHistory, { role: "assistant", content: reply }]);
    } catch {
      setChatHistory([...newHistory, { role: "assistant", content: "Sorry, something went wrong. Please try again." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const onChatKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSendChat();
    }
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
                {priceStats.delta <= 0 ? "Dropping" : "Rising"} ({priceStats.delta >= 0 ? "+" : ""}{priceStats.delta.toFixed(2)})
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
        {/* Watchlist form */}
        <form onSubmit={onAddWatchlist} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">Target price</h3>
          <p className="mt-1 text-sm text-slate-600">Save this item at your ideal price.</p>
          <input
            type="number"
            min="1"
            step="0.01"
            className="mt-3 w-full rounded-xl border border-slate-200 px-3 py-2 outline-none ring-sky-200 transition focus:ring-2"
            placeholder="e.g. 1199.99"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
          />
          <button
            type="submit"
            className="mt-3 rounded-xl bg-indigo-600 px-3 py-2 font-medium text-white transition hover:bg-indigo-700"
          >
            Save target
          </button>
          {watchlistMsg && <p className="mt-2 text-sm font-medium text-emerald-700">{watchlistMsg}</p>}
        </form>

        {/* AI Chat */}
        <div className="flex flex-col rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">Ask AI</h3>
          <p className="mt-1 text-sm text-slate-600">Ask about price trends, best time to buy, and more.</p>

          <div className="mt-3 flex flex-1 flex-col gap-2 overflow-y-auto max-h-64 min-h-[120px] rounded-xl bg-slate-50 p-3">
            {chatHistory.length === 0 && (
              <p className="text-xs text-slate-400 text-center mt-4">
                Try: "Is now a good time to buy?" or "When was the lowest price?"
              </p>
            )}
            {chatHistory.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <p
                  className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-white border border-slate-200 text-slate-700"
                  }`}
                >
                  {msg.content}
                </p>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <p className="rounded-2xl bg-white border border-slate-200 px-3 py-2 text-sm text-slate-400">
                  Thinking...
                </p>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>

          <div className="mt-3 flex gap-2">
            <input
              type="text"
              className="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none ring-indigo-200 transition focus:ring-2"
              placeholder="Ask a question..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={onChatKeyDown}
              disabled={chatLoading}
            />
            <button
              onClick={onSendChat}
              disabled={chatLoading || !chatInput.trim()}
              className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-40"
            >
              Send
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
