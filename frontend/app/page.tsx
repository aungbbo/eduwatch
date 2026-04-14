"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { fetchItems } from "@/lib/api";
import { Item } from "@/types";

const CATEGORIES = ["All", "Textbook", "Stationery", "Gadgets"];
const formatCurrency = (value?: number | null) =>
  typeof value === "number" ? `$${value.toFixed(2)}` : "N/A";

function getAffordabilityBand(price?: number | null) {
  if (price == null) return { label: "Unknown", tone: "text-slate-600 bg-slate-100" };
  if (price < 20) return { label: "Very affordable", tone: "text-emerald-700 bg-emerald-50" };
  if (price < 60) return { label: "Moderate", tone: "text-amber-700 bg-amber-50" };
  return { label: "High cost", tone: "text-rose-700 bg-rose-50" };
}

export default function HomePage() {
  const [items, setItems] = useState<Item[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [maxPrice, setMaxPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadItems = async (params?: { search?: string; category?: string; maxPrice?: number }) => {
    setLoading(true);
    setError("");
    try {
      const resolvedSearch =
        params && "search" in params
          ? params.search
          : search
            ? search
            : undefined;

      const data = await fetchItems({
        search: resolvedSearch,
        category: params?.category ?? category,
        maxPrice: params?.maxPrice ?? (maxPrice ? Number(maxPrice) : undefined)
      });
      setItems(data);
    } catch (err) {
      setError("Could not load items. Is backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await loadItems({
      search: search || undefined,
      category,
      maxPrice: maxPrice ? Number(maxPrice) : undefined
    });
  };

  const pricedItems = items.filter((item) => typeof item.lowest_price === "number");
  const cheapestItem = [...pricedItems].sort(
    (a, b) => (a.lowest_price ?? Number.MAX_VALUE) - (b.lowest_price ?? Number.MAX_VALUE)
  )[0];
  const averagePrice =
    pricedItems.length > 0
      ? pricedItems.reduce((acc, item) => acc + (item.lowest_price ?? 0), 0) / pricedItems.length
      : null;

  return (
    <main className="mx-auto max-w-6xl p-6 md:p-8">
      <section className="rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-700 via-blue-700 to-sky-600 p-6 text-white shadow-lg md:p-8">
        <h1 className="mt-2 text-3xl font-bold md:text-4xl">EduWatch</h1>
        <p className="mt-3 max-w-2xl text-sky-100">
          Save more on student essentials.
        </p>
        <div className="mt-6 grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl bg-white/15 p-4 backdrop-blur-sm">
            <p className="text-xs text-blue-100">Items</p>
            <p className="mt-1 text-2xl font-semibold">{items.length}</p>
          </div>
          <div className="rounded-2xl bg-white/15 p-4 backdrop-blur-sm">
            <p className="text-xs text-blue-100">Average price</p>
            <p className="mt-1 text-2xl font-semibold">{formatCurrency(averagePrice ?? undefined)}</p>
          </div>
          <div className="rounded-2xl bg-white/15 p-4 backdrop-blur-sm">
            <p className="text-xs text-blue-100">Best deal</p>
            <p className="mt-1 text-base font-semibold">
              {cheapestItem ? `${cheapestItem.name} (${formatCurrency(cheapestItem.lowest_price)})` : "No pricing data"}
            </p>
          </div>
        </div>
      </section>

      <form
        onSubmit={onSubmit}
        className="mt-6 grid gap-3 rounded-2xl border border-slate-200 bg-white/95 p-4 shadow-sm md:grid-cols-4"
      >
        <input
          className="rounded-xl border border-slate-200 px-3 py-2 outline-none ring-indigo-200 transition focus:ring-2"
          placeholder="Search items"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="rounded-xl border border-slate-200 px-3 py-2 outline-none ring-indigo-200 transition focus:ring-2"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <input
          className="rounded-xl border border-slate-200 px-3 py-2 outline-none ring-indigo-200 transition focus:ring-2"
          type="number"
          min="1"
          placeholder="Max budget"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
        <button
          className="rounded-xl bg-indigo-600 px-3 py-2 font-medium text-white transition hover:bg-indigo-700"
          type="submit"
        >
          Search
        </button>
      </form>

      {loading && <p className="mt-4 rounded-lg bg-white p-3 text-slate-700">Loading items...</p>}
      {error && <p className="mt-4 rounded-lg bg-rose-50 p-3 text-rose-700">{error}</p>}

      {!loading && !error && (
        <section className="mt-6 grid gap-4 md:grid-cols-2">
          {items.map((item) => (
            <Link
              href={`/item/${item.id}`}
              key={item.id}
              className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
            >
              <p className="inline-flex rounded-full bg-sky-50 px-2 py-1 text-xs font-medium text-sky-700">
                {item.category}
              </p>
              <h2 className="mt-3 text-lg font-semibold text-slate-900">{item.name}</h2>
              <p className="mt-2 text-sm text-slate-600">{item.description || "No description available."}</p>
              <div className="mt-4 flex items-center justify-between gap-3">
                <p className="font-semibold text-emerald-700">Best price: {formatCurrency(item.lowest_price)}</p>
                <span
                  className={`rounded-full px-2 py-1 text-xs font-medium ${getAffordabilityBand(item.lowest_price).tone}`}
                >
                  {getAffordabilityBand(item.lowest_price).label}
                </span>
              </div>
              <p className="mt-3 text-sm font-medium text-indigo-700 group-hover:text-indigo-800">
                View details ->
              </p>
            </Link>
          ))}
          {items.length === 0 && (
            <p className="rounded-lg border border-dashed border-slate-300 bg-white p-4 text-slate-600">
              No items found. Try fewer filters.
            </p>
          )}
        </section>
      )}
    </main>
  );
}
