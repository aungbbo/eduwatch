"""
RAG module: builds and queries a ChromaDB knowledge base.

Three collections:
  - item_prices: one document per item summarising price history
  - user_watchlist: one document per watchlist entry
  - sale_events: curated annual discount events with historical patterns
"""

from __future__ import annotations

from datetime import datetime, timedelta

import chromadb

_client = chromadb.PersistentClient(path="./chroma_db")
_item_col = _client.get_or_create_collection("item_prices")
_watch_col = _client.get_or_create_collection("user_watchlist")
_events_col = _client.get_or_create_collection("sale_events")


# ---------------------------------------------------------------------------
# Curated sale event knowledge
# ---------------------------------------------------------------------------

SALE_EVENTS = [
    {
        "id": "black-friday",
        "doc": (
            "Black Friday (last Friday of November each year): "
            "The biggest discount event of the year for consumer electronics. "
            "Historically sees 15-30% price drops across most product categories. "
            "EduWatch historical data: "
            "MacBook Pro M4 dropped to $1,299 on Nov 28, 2024 and again on Nov 28, 2025 (all-time low). "
            "Apple Watch SE 3 dropped to $199 on Nov 28, 2025 (all-time low, $50 off normal price). "
            "Sony WH-1000XM5 dropped to $299.99 on Nov 28, 2024 and $279.99 on Nov 28, 2025 (all-time low). "
            "TI-84 Plus dropped to $89.99 on Nov 28, 2024 and $84.99 on Nov 28, 2025 (all-time low). "
            "Recommendation: if current price is near the all-time high and Black Friday is within 2 months, waiting is usually worth it."
        ),
    },
    {
        "id": "cyber-monday",
        "doc": (
            "Cyber Monday (Monday after Black Friday, late November): "
            "Online-focused sale event following Black Friday. "
            "Discounts are similar to or slightly less than Black Friday, typically 10-20%. "
            "Best for: laptops, headphones, and accessories. "
            "Often a second chance to buy if you missed Black Friday deals. "
            "Recommendation: if you missed Black Friday, Cyber Monday is the next best opportunity."
        ),
    },
    {
        "id": "back-to-school",
        "doc": (
            "Back-to-School season (July and August each year): "
            "Second-biggest discount period for student electronics and supplies. "
            "Retailers target students heading into fall semester. "
            "Typical discounts: 10-20% on laptops, calculators, and accessories. "
            "EduWatch historical data: "
            "MacBook Pro M4 dropped to $1,399 in Jul-Aug 2025 (down $200 from normal $1,599). "
            "TI-84 Plus dropped to $94.99 in Jul-Aug 2025 (down $15 from normal $109.99). "
            "Recommendation: great time to buy student essentials if you cannot wait for Black Friday."
        ),
    },
    {
        "id": "post-holiday",
        "doc": (
            "Post-Holiday Clearance (late December through January): "
            "Prices often stay low or drop further after Christmas as retailers clear inventory. "
            "EduWatch historical data: "
            "MacBook Pro M4 held at $1,299-$1,399 through December 2025 and January 2026. "
            "Recommendation: if you missed Black Friday, prices often remain discounted through January."
        ),
    },
    {
        "id": "prime-day",
        "doc": (
            "Amazon Prime Day (typically mid-July each year): "
            "Major Amazon-exclusive sale event. "
            "Electronics see 10-25% discounts, particularly strong for headphones and accessories. "
            "Not always reflected in multi-store comparisons since it is Amazon-only. "
            "Recommendation: good opportunity for Amazon purchases, especially Sony headphones and Apple products."
        ),
    },
    {
        "id": "spring-no-sale",
        "doc": (
            "Spring (March through May): "
            "Generally not a major discount period for electronics. "
            "Prices tend to be at or near normal levels. "
            "EduWatch data confirms: MacBook Pro and Apple Watch prices were at $1,299-$1,349 and $219-$239 in spring 2026 — "
            "not at their lowest, but MacBook is near its all-time low of $1,299. "
            "Recommendation: spring is not an ideal time to wait for a sale. "
            "If current price is near all-time low, buying now may be better than waiting for back-to-school in July."
        ),
    },
]


# ---------------------------------------------------------------------------
# Indexing helpers
# ---------------------------------------------------------------------------

def _item_doc(item, recent_snapshots, all_time_low: float, all_time_high: float) -> str:
    """Build a natural-language summary for one item."""
    prices = [s.price for s in recent_snapshots]
    if not prices:
        return f"Item: {item.name} ({item.category}). No price data available yet."

    current = prices[0]
    avg = round(sum(prices) / len(prices), 2)

    # Find notable drops from recent history: price fell ≥5% vs previous snapshot
    notable: list[str] = []
    sorted_snaps = sorted(recent_snapshots, key=lambda s: s.captured_at)
    prev_price = None
    for snap in sorted_snaps:
        if prev_price is not None and snap.price < prev_price * 0.95:
            notable.append(
                f"{snap.captured_at.strftime('%b %Y')} dropped to ${snap.price:.2f}"
            )
        prev_price = snap.price

    notable_str = "; ".join(notable[-3:]) if notable else "no major drops in recent history"

    oldest = sorted_snaps[0].captured_at.strftime("%b %d, %Y") if sorted_snaps else "N/A"
    newest = sorted_snaps[-1].captured_at.strftime("%b %d, %Y") if sorted_snaps else "N/A"

    return (
        f"Item: {item.name} (category: {item.category}).\n"
        f"Description: {item.description}.\n"
        f"Current price: ${current:.2f}. "
        f"All-time low: ${all_time_low:.2f}. "
        f"All-time high: ${all_time_high:.2f}. "
        f"Recent average (last 120 snapshots): ${avg:.2f}.\n"
        f"Price data from {oldest} to {newest}.\n"
        f"Notable price drops: {notable_str}."
    )


def _watchlist_doc(entry, item_name: str, current_price: float | None) -> str:
    """Build a natural-language summary for one watchlist entry."""
    gap = None
    if current_price is not None:
        gap = round(current_price - entry.target_price, 2)

    gap_str = (
        f"${abs(gap):.2f} {'above' if gap > 0 else 'below'} target"
        if gap is not None else "unknown"
    )
    met = gap is not None and gap <= 0

    return (
        f"User {entry.user_tag} is watching {item_name}.\n"
        f"Target price: ${entry.target_price:.2f}. "
        f"Current price: ${f'{current_price:.2f}' if current_price is not None else 'unknown'}. "
        f"Gap: {gap_str}.\n"
        f"Target {'has been met' if met else 'not yet met'}. "
        f"Added on {entry.created_at.strftime('%b %d, %Y')}."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_event_index() -> None:
    """Index curated sale events. Safe to call multiple times."""
    for event in SALE_EVENTS:
        _events_col.upsert(documents=[event["doc"]], ids=[event["id"]])
    print(f"[RAG] Indexed {len(SALE_EVENTS)} sale events.")


def build_index(db) -> None:
    """Index all items, watchlist entries, and sale events. Safe to call multiple times."""
    from sqlalchemy import func as sqlfunc
    from .models import Item, PriceSnapshot, WatchlistEntry

    # Clear stale watchlist docs so deleted entries don't persist in ChromaDB
    existing_watch = _watch_col.get()
    if existing_watch["ids"]:
        _watch_col.delete(ids=existing_watch["ids"])

    items = db.query(Item).all()
    for item in items:
        # Recent snapshots for trend/average analysis
        recent_snapshots = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.item_id == item.id)
            .order_by(PriceSnapshot.captured_at.desc())
            .limit(120)
            .all()
        )
        # True all-time min/max from the full history
        all_time_low = (
            db.query(sqlfunc.min(PriceSnapshot.price))
            .filter(PriceSnapshot.item_id == item.id)
            .scalar() or 0.0
        )
        all_time_high = (
            db.query(sqlfunc.max(PriceSnapshot.price))
            .filter(PriceSnapshot.item_id == item.id)
            .scalar() or 0.0
        )
        doc = _item_doc(item, recent_snapshots, all_time_low, all_time_high)
        _item_col.upsert(documents=[doc], ids=[f"item-{item.id}"])

    entries = db.query(WatchlistEntry).all()
    item_map = {i.id: i.name for i in items}
    for entry in entries:
        latest = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.item_id == entry.item_id)
            .order_by(PriceSnapshot.captured_at.desc())
            .first()
        )
        current_price = latest.price if latest else None
        doc = _watchlist_doc(entry, item_map.get(entry.item_id, f"Item #{entry.item_id}"), current_price)
        _watch_col.upsert(
            documents=[doc],
            ids=[f"watch-{entry.id}"],
            metadatas=[{"user_tag": entry.user_tag, "item_id": int(entry.item_id)}],
        )

    build_event_index()
    print(f"[RAG] Indexed {len(items)} items and {len(entries)} watchlist entries.")


def upsert_watchlist_entry(entry, item_name: str, current_price: float | None) -> None:
    """Call this immediately after a new watchlist entry is saved."""
    doc = _watchlist_doc(entry, item_name, current_price)
    # Store item_id as int — Chroma may return it as float/str; compare flexibly in retrieve
    _watch_col.upsert(
        documents=[doc],
        ids=[f"watch-{entry.id}"],
        metadatas=[{"user_tag": entry.user_tag, "item_id": int(entry.item_id)}],
    )


def _meta_item_matches(meta: dict, user_tag: str, item_id: int) -> bool:
    if meta.get("user_tag") != user_tag:
        return False
    raw = meta.get("item_id")
    if raw is None:
        return False
    try:
        return int(float(raw)) == int(item_id)
    except (TypeError, ValueError):
        return False


def full_watchlist_section_from_db(db, user_tag: str, current_item_id: int | None) -> str:
    """One line per watched item with target + current price; mark which item the user is viewing."""
    from .models import Item, PriceSnapshot, WatchlistEntry

    rows = (
        db.query(WatchlistEntry)
        .filter(WatchlistEntry.user_tag == user_tag)
        .order_by(WatchlistEntry.created_at.desc())
        .all()
    )
    if not rows:
        return "[ALL ITEMS ON USER WATCHLIST]\nNo items saved."

    seen: set[int] = set()
    lines: list[str] = []
    for entry in rows:
        if entry.item_id in seen:
            continue
        seen.add(entry.item_id)

        it = db.query(Item).filter(Item.id == entry.item_id).first()
        name = it.name if it else f"Item #{entry.item_id}"
        latest = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.item_id == entry.item_id)
            .order_by(PriceSnapshot.captured_at.desc())
            .first()
        )
        cur = f"${latest.price:.2f}" if latest else "unknown"
        viewing = (
            " — THIS IS THE ITEM THE USER IS VIEWING NOW"
            if current_item_id is not None and entry.item_id == current_item_id
            else ""
        )
        lines.append(
            f"- {name}: target ${entry.target_price:.2f}, current price {cur}{viewing}"
        )

    body = "\n".join(lines)
    return f"[ALL ITEMS ON USER WATCHLIST]\n{body}"


def watchlist_section_from_db(db, user_tag: str, item_id: int) -> str:
    """Live SQLite lookup — always matches what the user just saved (source of truth for chat)."""
    from .models import Item, PriceSnapshot, WatchlistEntry

    entry = (
        db.query(WatchlistEntry)
        .filter(WatchlistEntry.user_tag == user_tag, WatchlistEntry.item_id == item_id)
        .order_by(WatchlistEntry.created_at.desc())
        .first()
    )
    if entry is None:
        return "[USER WATCHLIST FOR THIS ITEM]\nNo watchlist entry set for this item."

    item = db.query(Item).filter(Item.id == item_id).first()
    latest = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.item_id == item_id)
        .order_by(PriceSnapshot.captured_at.desc())
        .first()
    )
    current_price = latest.price if latest else None
    doc = _watchlist_doc(
        entry,
        item.name if item else f"Item #{item_id}",
        current_price,
    )
    return f"[USER WATCHLIST FOR THIS ITEM]\n{doc}"


def retrieve_context(
    question: str,
    user_tag: str,
    item_id: int | None = None,
    db=None,
) -> str:
    """
    Retrieve relevant context chunks for a user question.
    Each section is clearly labeled so the LLM knows what it represents.
    """
    from datetime import date
    today = date.today().strftime("%B %d, %Y")
    sections: list[str] = [f"[TODAY'S DATE]\n{today}"]

    # 1. Current item price data
    if item_id is not None:
        try:
            specific = _item_col.get(ids=[f"item-{item_id}"])
            if specific["documents"]:
                sections.append(f"[CURRENT ITEM PRICE DATA]\n{specific['documents'][0]}")
        except Exception:
            pass

    # 2. User's watchlist — prefer live DB (instant after POST /watchlist); else Chroma fallback
    if item_id is not None:
        if db is not None:
            watchlist_section = watchlist_section_from_db(db, user_tag, item_id)
        else:
            watchlist_section = "[USER WATCHLIST FOR THIS ITEM]\nNo watchlist entry set for this item."
            try:
                all_watch = _watch_col.get(include=["documents", "metadatas"])
                for doc, meta in zip(
                    all_watch["documents"],
                    all_watch["metadatas"] or [{}] * len(all_watch["documents"]),
                ):
                    if _meta_item_matches(meta or {}, user_tag, item_id):
                        watchlist_section = f"[USER WATCHLIST FOR THIS ITEM]\n{doc}"
                        break
            except Exception:
                pass
    else:
        watchlist_section = "[USER WATCHLIST FOR THIS ITEM]\nNo watchlist entry set for this item."
    sections.append(watchlist_section)

    # 2b. Full watchlist (all items) so the model can answer "what am I watching?" from Mac detail page
    if db is not None:
        sections.append(full_watchlist_section_from_db(db, user_tag, item_id))

    # 3. Relevant sale events (top 2)
    try:
        event_results = _events_col.query(query_texts=[question], n_results=2)
        event_docs = event_results["documents"][0]
        if event_docs:
            sections.append(f"[RELEVANT SALE EVENTS]\n" + "\n\n".join(event_docs))
    except Exception:
        pass

    return "\n\n---\n\n".join(sections)
