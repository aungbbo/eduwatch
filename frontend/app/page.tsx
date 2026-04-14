"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { fetchItems } from "@/lib/api";
import { Item } from "@/types";

const CATEGORIES = ["all", "textbook", "stationery", "gadgets"];

export default function HomePage() {
  const [items, setItems] = useState<Item[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [maxPrice, setMaxPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadItems = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchItems({
        search: search || undefined,
        category,
        maxPrice: maxPrice ? Number(maxPrice) : undefined
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
    await loadItems();
  };

  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-3xl font-bold">EduWatch</h1>
      <p className="mt-2 text-slate-600">Track prices for student essentials and find affordable deals.</p>

      <form onSubmit={onSubmit} className="mt-6 grid gap-3 rounded border bg-white p-4 md:grid-cols-4">
        <input
          className="rounded border px-3 py-2"
          placeholder="Search item..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="rounded border px-3 py-2"
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
          className="rounded border px-3 py-2"
          type="number"
          min="1"
          placeholder="Max budget"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
        <button className="rounded bg-slate-900 px-3 py-2 font-medium text-white" type="submit">
          Apply Filters
        </button>
      </form>

      {loading && <p className="mt-4">Loading...</p>}
      {error && <p className="mt-4 text-red-600">{error}</p>}

      {!loading && !error && (
        <section className="mt-6 grid gap-4 md:grid-cols-2">
          {items.map((item) => (
            <Link href={`/item/${item.id}`} key={item.id} className="rounded border bg-white p-4 hover:shadow">
              <p className="text-sm text-slate-500">{item.category}</p>
              <h2 className="text-lg font-semibold">{item.name}</h2>
              <p className="mt-2 text-sm text-slate-700">{item.description || "No description"}</p>
              <p className="mt-3 font-medium text-emerald-700">
                Best Price: {item.lowest_price ? `$${item.lowest_price.toFixed(2)}` : "N/A"}
              </p>
            </Link>
          ))}
          {items.length === 0 && <p className="text-slate-600">No items match your filters.</p>}
        </section>
      )}
    </main>
  );
}
