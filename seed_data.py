from datetime import datetime
from pathlib import Path

from models import Clothing, Electronics, HomeGoods, Order, OrderLine, StoreData

DATA_PATH = Path(__file__).parent / "data" / "store.pkl"


def make_products():
    return [
        # id, name, price, stock, image, extra detail, (old price), (is_new)
        Electronics(1, "Earbuds", 7999, 25, "earbuds.png", 12),
        Electronics(2, "LED Desk Lamp", 2999, 12, "desk_lamp.png", 6, is_new=True),
        Electronics(3, "Bluetooth Speaker", 4999, 8, "speaker.png", 12, old_price_cents=6999),
        Electronics(4, "Smart Watch", 12999, 5, "smart_watch.png", 24, is_new=True),
        Electronics(5, "Power Bank", 2499, 0, "power_bank.png", 6),
        Clothing(6, "Oversized Hoodie", 3999, 15, "hoodie.png", ["S", "M", "L", "XL"]),
        Clothing(7, "Denim Jacket", 5999, 6, "denim_jacket.png", ["M", "L"], old_price_cents=7999),
        Clothing(8, "Running Sneakers", 8999, 10, "sneakers.png", ["40", "41", "42", "43"], is_new=True),
        Clothing(9, "Baseball Cap", 1499, 30, "cap.png", ["One size"]),
        Clothing(10, "Basic T-Shirt", 999, 40, "tshirt.png", ["S", "M", "L"], old_price_cents=1499),
        HomeGoods(11, "Water Bottle", 1999, 20, "water_bottle.png", "Stainless steel"),
        HomeGoods(12, "Ceramic Mug", 1299, 18, "mug.png", "Ceramic"),
        HomeGoods(13, "Throw Pillow", 2299, 9, "pillow.png", "Cotton", old_price_cents=2999),
        HomeGoods(14, "Scented Candle", 1599, 3, "candle.png", "Soy wax", is_new=True),
        HomeGoods(15, "Wall Clock", 3499, 7, "wall_clock.png", "Wood"),
    ]

def hours_ago(now, hours):
    return datetime.fromtimestamp(now.timestamp() - hours * 3600)

def make_sample_orders(products, now):
    specs = [
        ("ALB-10203", hours_ago(now, 240), [(4, 1)]),
        ("ALB-10276", hours_ago(now, 48), [(6, 1), (11, 1)]),
        ("ALB-10318", hours_ago(now, 3), [(1, 1), (2, 1)]),
    ]
    orders = []
    for order_id, placed_at, items in specs:
        lines = []
        subtotal = 0
        for product_id, quantity in items:
            p = products[product_id]
            line = OrderLine(p.id, p.name, p.image_file, p.price_cents, quantity)
            lines.append(line)
            subtotal += line.line_total_cents()
        orders.append(Order(order_id, placed_at, lines, subtotal, 0))
    return orders

def make_default_data():
    products = {}
    for p in make_products():
        products[p.id] = p
    orders = make_sample_orders(products, datetime.now())
    return StoreData(products, orders, 10319)

if __name__ == "__main__":
    import storage

    storage.save(make_default_data(), DATA_PATH)
    print(f"Reset data saved to {DATA_PATH}")
