from datetime import datetime, timedelta
from random import uniform

from app.database import Base, SessionLocal, engine
from app.models import Item, PriceSnapshot

Base.metadata.create_all(bind=engine)

ITEMS = [
    ("Calculus Textbook", "textbook", "Used-friendly calculus book"),
    ("Notebook Pack", "stationery", "5-pack college ruled notebooks"),
    ("Graphing Calculator", "gadgets", "Scientific graphing calculator"),
    ("Blue Pen Set", "stationery", "Pack of 20 blue pens"),
    ("Laptop 13-inch", "gadgets", "Entry-level student laptop"),
]

STORES = ["CampusStore", "BudgetMart", "BookHub"]


def seed():
    db = SessionLocal()
    try:
        if db.query(Item).count() > 0:
            print("Seed skipped: items already exist.")
            return

        created_items = []
        for name, category, description in ITEMS:
            item = Item(name=name, category=category, description=description)
            db.add(item)
            db.flush()
            created_items.append(item)

        db.commit()

        now = datetime.utcnow()
        for item in created_items:
            base_price = uniform(8.0, 120.0)
            for day in range(10, -1, -1):
                for store in STORES:
                    jitter = uniform(-6.0, 6.0)
                    snap = PriceSnapshot(
                        item_id=item.id,
                        store=store,
                        price=round(max(1.0, base_price + jitter), 2),
                        currency="USD",
                        in_stock=True,
                        captured_at=now - timedelta(days=day),
                    )
                    db.add(snap)
        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
