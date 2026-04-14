from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)

    price_snapshots = relationship("PriceSnapshot", back_populates="item")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    store = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    currency = Column(String, nullable=False, default="USD")
    in_stock = Column(Boolean, nullable=False, default=True)
    captured_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    item = relationship("Item", back_populates="price_snapshots")


class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_tag = Column(String, nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
