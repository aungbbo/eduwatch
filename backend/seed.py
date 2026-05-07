from datetime import date, datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Item, PriceSnapshot

Base.metadata.create_all(bind=engine)


def date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


ITEMS_DATA = [
    {
        "name": "MacBook Pro M4",
        "category": "gadgets",
        "description": "Apple MacBook Pro 14-inch with M4 chip",
        "stores": {"Amazon": 0, "Best Buy": 10.00, "Apple Store": 0},
        "price_history": [
            (date(2024, 10, 30), date(2024, 11, 28), 1599.00),
            (date(2024, 11, 29), date(2024, 12, 2),  1499.00),
            (date(2024, 12, 3),  date(2024, 12, 24), 1549.00),
            (date(2024, 12, 25), date(2025, 1, 15),  1499.00),
            (date(2025, 1, 16),  date(2025, 3, 31),  1599.00),
            (date(2025, 4, 1),   date(2025, 7, 10),  1499.00),
            (date(2025, 7, 11),  date(2025, 8, 31),  1399.00),
            (date(2025, 9, 1),   date(2025, 11, 27), 1499.00),
            (date(2025, 11, 28), date(2025, 12, 2),  1299.00),
            (date(2025, 12, 3),  date(2026, 1, 20),  1399.00),
            (date(2026, 1, 21),  date(2026, 3, 31),  1349.00),
            (date(2026, 4, 1),   date(2026, 5, 6),   1299.00),
        ],
    },
    {
        "name": "Apple Watch SE 3",
        "category": "gadgets",
        "description": "Apple Watch SE 3rd generation with GPS",
        "stores": {"Amazon": 0, "Best Buy": 5.00, "Apple Store": 0},
        "price_history": [
            (date(2025, 9, 19),  date(2025, 10, 31), 249.00),
            (date(2025, 11, 1),  date(2025, 11, 27), 239.00),
            (date(2025, 11, 28), date(2025, 12, 2),  199.00),
            (date(2025, 12, 3),  date(2025, 12, 24), 219.00),
            (date(2025, 12, 25), date(2026, 1, 15),  229.00),
            (date(2026, 1, 16),  date(2026, 2, 5),   239.00),
            (date(2026, 2, 6),   date(2026, 3, 9),   219.00),
            (date(2026, 3, 10),  date(2026, 3, 14),  239.00),
            (date(2026, 3, 15),  date(2026, 3, 31),  219.00),
            (date(2026, 4, 1),   date(2026, 4, 6),   239.00),
            (date(2026, 4, 7),   date(2026, 4, 10),  239.99),
            (date(2026, 4, 11),  date(2026, 4, 20),  219.00),
            (date(2026, 4, 21),  date(2026, 4, 24),  239.00),
            (date(2026, 4, 25),  date(2026, 5, 6),   219.00),
        ],
    },
    {
        "name": "Sony WH-1000XM5",
        "category": "gadgets",
        "description": "Sony WH-1000XM5 wireless noise-cancelling headphones",
        "stores": {"Amazon": 0, "Best Buy": 10.00, "Sony Store": 0},
        "price_history": [
            (date(2024, 5, 6),   date(2024, 6, 15),  399.99),
            (date(2024, 6, 16),  date(2024, 7, 10),  349.99),
            (date(2024, 7, 11),  date(2024, 9, 30),  399.99),
            (date(2024, 10, 1),  date(2024, 11, 27), 349.99),
            (date(2024, 11, 28), date(2024, 12, 2),  299.99),
            (date(2024, 12, 3),  date(2025, 1, 10),  328.00),
            (date(2025, 1, 11),  date(2025, 4, 30),  349.99),
            (date(2025, 5, 1),   date(2025, 7, 15),  328.00),
            (date(2025, 7, 16),  date(2025, 9, 30),  299.99),
            (date(2025, 10, 1),  date(2025, 11, 27), 348.00),
            (date(2025, 11, 28), date(2025, 12, 2),  279.99),
            (date(2025, 12, 3),  date(2026, 2, 28),  298.00),
            (date(2026, 3, 1),   date(2026, 5, 6),   279.99),
        ],
    },
    {
        "name": "Texas Instruments TI-84 Plus",
        "category": "gadgets",
        "description": "TI-84 Plus graphing calculator for math and science",
        "stores": {"Amazon": 0, "Walmart": -5.00, "Staples": 5.00},
        "price_history": [
            (date(2024, 5, 6),   date(2024, 8, 15),  119.99),
            (date(2024, 8, 16),  date(2024, 9, 15),  99.99),
            (date(2024, 9, 16),  date(2024, 11, 27), 109.99),
            (date(2024, 11, 28), date(2024, 12, 2),  89.99),
            (date(2024, 12, 3),  date(2025, 1, 31),  99.99),
            (date(2025, 2, 1),   date(2025, 7, 15),  109.99),
            (date(2025, 7, 16),  date(2025, 8, 31),  94.99),
            (date(2025, 9, 1),   date(2025, 11, 27), 109.99),
            (date(2025, 11, 28), date(2025, 12, 2),  84.99),
            (date(2025, 12, 3),  date(2026, 1, 15),  99.99),
            (date(2026, 1, 16),  date(2026, 3, 31),  104.99),
            (date(2026, 4, 1),   date(2026, 5, 6),   99.99),
        ],
    },
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Item).count() > 0:
            print("Seed skipped: items already exist.")
            return

        for item_data in ITEMS_DATA:
            item = Item(
                name=item_data["name"],
                category=item_data["category"],
                description=item_data["description"],
            )
            db.add(item)
            db.flush()

            for store_name, offset in item_data["stores"].items():
                for start, end, base_price in item_data["price_history"]:
                    for d in date_range(start, end):
                        snap = PriceSnapshot(
                            item_id=item.id,
                            store=store_name,
                            price=round(base_price + offset, 2),
                            currency="USD",
                            in_stock=True,
                            captured_at=datetime(d.year, d.month, d.day, 12, 0, 0),
                        )
                        db.add(snap)

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
