import os
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item, PriceSnapshot, WatchlistEntry
from .rag import build_index, retrieve_context, upsert_watchlist_entry
from .schemas import ItemDetailOut, ItemOut, WatchlistCreate, WatchlistOut

load_dotenv()
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        build_index(db)
    finally:
        db.close()
    yield


app = FastAPI(title="EduWatch API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/items", response_model=list[ItemOut])
def list_items(
    search: str | None = None,
    category: str | None = None,
    max_price: float | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    query = db.query(Item)
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Item.category == category)

    items = query.all()
    output: list[ItemOut] = []
    for item in items:
        lowest_price = (
            db.query(func.min(PriceSnapshot.price))
            .filter(PriceSnapshot.item_id == item.id)
            .scalar()
        )
        if max_price is not None and lowest_price is not None and lowest_price > max_price:
            continue

        latest_snapshot = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.item_id == item.id)
            .order_by(PriceSnapshot.captured_at.desc())
            .first()
        )
        current_price = latest_snapshot.price if latest_snapshot else None

        output.append(
            ItemOut(
                id=item.id,
                name=item.name,
                category=item.category,
                description=item.description,
                lowest_price=lowest_price,
                current_price=current_price,
            )
        )
    return output


@app.get("/items/{item_id}", response_model=ItemDetailOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    history = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.item_id == item.id)
        .order_by(PriceSnapshot.captured_at.asc())
        .all()
    )
    lowest_price = min((s.price for s in history), default=None)

    return ItemDetailOut(
        id=item.id,
        name=item.name,
        category=item.category,
        description=item.description,
        lowest_price=lowest_price,
        price_history=history,
    )


@app.get("/items/{item_id}/history")
def get_item_history(item_id: int, db: Session = Depends(get_db)):
    history = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.item_id == item_id)
        .order_by(PriceSnapshot.captured_at.asc())
        .all()
    )
    return history


@app.post("/watchlist", response_model=WatchlistOut)
def add_watchlist_entry(payload: WatchlistCreate, db: Session = Depends(get_db)):
    entry = WatchlistEntry(
        user_tag=payload.user_tag, item_id=payload.item_id, target_price=payload.target_price
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Index into RAG immediately so AI knows about this target
    item = db.query(Item).filter(Item.id == payload.item_id).first()
    latest = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.item_id == payload.item_id)
        .order_by(PriceSnapshot.captured_at.desc())
        .first()
    )
    upsert_watchlist_entry(
        entry,
        item_name=item.name if item else f"Item #{payload.item_id}",
        current_price=latest.price if latest else None,
    )

    return entry


@app.delete("/watchlist/{entry_id}", status_code=204)
def delete_watchlist_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(WatchlistEntry).filter(WatchlistEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")
    db.delete(entry)
    db.commit()
    # Remove from ChromaDB too
    try:
        from .rag import _watch_col
        _watch_col.delete(ids=[f"watch-{entry_id}"])
    except Exception:
        pass


@app.get("/watchlist/{user_tag}", response_model=list[WatchlistOut])
def get_watchlist(user_tag: str, db: Session = Depends(get_db)):
    entries = (
        db.query(WatchlistEntry)
        .filter(WatchlistEntry.user_tag == user_tag)
        .order_by(WatchlistEntry.created_at.desc())
        .all()
    )
    return entries


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    user_tag: str = "demo-student"


@app.post("/chat/{item_id}")
def chat(item_id: int, payload: ChatRequest, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Retrieve personalized context from ChromaDB
    rag_context = retrieve_context(
        question=payload.message,
        user_tag=payload.user_tag,
        item_id=item_id,
    )

    system_prompt = f"""You are EduWatch AI, a smart shopping assistant that helps students decide when to buy products.

The user is currently viewing: {item.name}.

Below is structured context retrieved from our knowledge base. Each section is labeled — read them carefully and only use information from the correct section:

{rag_context}

Guidelines:
- Focus only on {item.name}. Do not mention other products unless the user explicitly asks.
- For watchlist information, use ONLY what is in [USER WATCHLIST FOR THIS ITEM]. If it says "No watchlist entry set", do not mention any target price or watchlist.
- For price data, use ONLY what is in [CURRENT ITEM PRICE DATA]. Do not invent prices.
- For sale timing advice, use [RELEVANT SALE EVENTS] and [TODAY'S DATE] to reason about how far away sales are.
- Be concise and friendly — 2-4 sentences unless more detail is needed."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in payload.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": payload.message})

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=512,
        temperature=0.7,
    )
    reply = response.choices[0].message.content
    return {"reply": reply}
