from abc import ABC, abstractmethod

from errors import OutOfStockError


SHIPPED_AFTER_HOURS = 24
DELIVERED_AFTER_HOURS = 72
LOW_STOCK_LIMIT = 5

def format_price(cents):
    return f"${cents // 100}.{cents % 100:02d}"


class Product(ABC):
    def __init__(self, id, name, category, price_cents, stock, image_file,
                 old_price_cents=0, is_new=False):
        self.id = id
        self.name = name
        self.category = category
        self.price_cents = price_cents
        self.stock = stock
        self.image_file = image_file
        self.old_price_cents = old_price_cents
        self.is_new = is_new

    def __str__(self):
        return f"{self.name} ({format_price(self.price_cents)})"

    @abstractmethod
    def details(self):
        pass

    def is_deal(self):
        return self.old_price_cents > self.price_cents

    def in_stock(self):
        return self.stock > 0

    def stock_label(self):
        if self.stock == 0:
            return "Out of Stock"
        if self.stock <= LOW_STOCK_LIMIT:
            return f"Only {self.stock} left"
        return "In Stock"

    def reduce_stock(self, quantity):
        if quantity > self.stock:
            raise OutOfStockError(self.name, self.stock)
        self.stock -= quantity

class Electronics(Product):
    def __init__(self, id, name, price_cents, stock, image_file, warranty_months,
                 old_price_cents=0, is_new=False):
        super().__init__(id, name, "Electronics", price_cents, stock, image_file,
                         old_price_cents, is_new)
        self.warranty_months = warranty_months

    def details(self):
        return [f"{self.warranty_months}-month warranty"]

class Clothing(Product):
    def __init__(self, id, name, price_cents, stock, image_file, sizes,
                 old_price_cents=0, is_new=False):
        super().__init__(id, name, "Clothing", price_cents, stock,
                         image_file, old_price_cents, is_new)
        self.sizes = sizes

    def details(self):
        return ["Sizes: " + ", ".join(self.sizes)]

class HomeGoods(Product):
    def __init__(self, id, name, price_cents, stock, image_file, material,
                 old_price_cents=0, is_new=False):
        super().__init__(id, name, "Home Goods", price_cents, stock, image_file,
                         old_price_cents, is_new)
        self.material = material

    def details(self):
        return [f"Material: {self.material}"]



class OrderLine:
    def __init__(self, product_id, name, image_file, unit_price_cents, quantity):
        self.product_id = product_id
        self.name = name
        self.image_file = image_file
        self.unit_price_cents = unit_price_cents
        self.quantity = quantity

    def line_total_cents(self):
        return self.unit_price_cents * self.quantity


class Order:
    def __init__(self, order_id, placed_at, lines, subtotal_cents, shipping_cents):
        self.order_id = order_id
        self.placed_at = placed_at
        self.lines = lines
        self.subtotal_cents = subtotal_cents
        self.shipping_cents = shipping_cents

    def __str__(self):
        return f"Order #{self.order_id}"

    def total_cents(self):
        return self.subtotal_cents + self.shipping_cents

    def item_count(self):
        count = 0
        for line in self.lines:
            count += line.quantity
        return count

    def status(self, now):
        age_hours = (now - self.placed_at).total_seconds() / 3600
        if age_hours < SHIPPED_AFTER_HOURS:
            return "Processing"
        if age_hours < DELIVERED_AFTER_HOURS:
            return "Shipped"
        return "Delivered"

class StoreData:
    def __init__(self, products, orders, next_order_number):
        self.products = products
        self.cart = {}
        self.orders = orders
        self.next_order_number = next_order_number
