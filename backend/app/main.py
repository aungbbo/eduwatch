from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item, PriceSnapshot, WatchlistEntry
from .schemas import ItemDetailOut, ItemOut, WatchlistCreate, WatchlistOut

app = FastAPI(title="EduWatch API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


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

        output.append(
            ItemOut(
                id=item.id,
                name=item.name,
                category=item.category,
                description=item.description,
                lowest_price=lowest_price,
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
    return entry


@app.get("/watchlist/{user_tag}", response_model=list[WatchlistOut])
def get_watchlist(user_tag: str, db: Session = Depends(get_db)):
    entries = (
        db.query(WatchlistEntry)
        .filter(WatchlistEntry.user_tag == user_tag)
        .order_by(WatchlistEntry.created_at.desc())
        .all()
    )
    return entries


@app.post("/insights/{item_id}")
def simple_insight(item_id: int, db: Session = Depends(get_db)):
    history = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.item_id == item_id)
        .order_by(PriceSnapshot.captured_at.desc())
        .limit(7)
        .all()
    )
    if not history:
        return {"recommendation": "No data yet. Track this item for a few days."}

    prices = [h.price for h in history]
    latest = prices[0]
    average = sum(prices) / len(prices)
    if latest <= average * 0.95:
        recommendation = "Price is below recent average. Good time to buy."
    else:
        recommendation = "Price is near or above recent average. Consider waiting."
    return {"recommendation": recommendation, "latest_price": latest, "recent_average": round(average, 2)}
