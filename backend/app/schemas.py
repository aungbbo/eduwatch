from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PriceSnapshotOut(BaseModel):
    id: int
    store: str
    price: float
    currency: str
    in_stock: bool
    captured_at: datetime

    class Config:
        from_attributes = True


class ItemOut(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None
    lowest_price: Optional[float] = None

    class Config:
        from_attributes = True


class ItemDetailOut(ItemOut):
    price_history: list[PriceSnapshotOut]


class WatchlistCreate(BaseModel):
    user_tag: str
    item_id: int
    target_price: float


class WatchlistOut(BaseModel):
    id: int
    user_tag: str
    item_id: int
    target_price: float
    created_at: datetime

    class Config:
        from_attributes = True
