import storage
from errors import EmptyCartError, OutOfStockError, ProductNotFoundError
from models import Order, OrderLine
from seed_data import make_default_data

SHIPPING_CENTS = 500
FREE_SHIPPING_MIN_CENTS = 5000

class Store:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = storage.load(data_path, make_default_data())

    def save(self):
        storage.save(self.data, self.data_path)

    def get_product(self, product_id):
        if product_id not in self.data.products:
            raise ProductNotFoundError(product_id)
        return self.data.products[product_id]


    def all_products(self):
        return list(self.data.products.values())

    def search(self, query):
        text = query.strip().lower()
        results = []
        if text == "":
            return results
        for p in self.data.products.values():
            if text in p.name.lower():
                results.append(p)
        return results

    def categories(self):
        names = []
        for p in self.data.products.values():
            if p.category not in names:
                names.append(p.category)
        names.sort()
        return names

    def by_category(self, category):
        results = []
        for p in self.data.products.values():
            if p.category == category:
                results.append(p)
        return results

    def deals(self):
        results = []
        for p in self.data.products.values():
            if p.is_deal():
                results.append(p)
        return results

    def new_arrivals(self):
        results = []
        for p in self.data.products.values():
            if p.is_new:
                results.append(p)
        return results

    def add_to_cart(self, product_id, quantity=1):
        current = self.data.cart.get(product_id, 0)
        self.set_quantity(product_id, current + quantity)

    def set_quantity(self, product_id, quantity):
        product = self.get_product(product_id)
        if quantity <= 0:
            self.remove_from_cart(product_id)
            return
        if quantity > product.stock:
            raise OutOfStockError(product.name, product.stock)
        self.data.cart[product_id] = quantity
        self.save()

    def remove_from_cart(self, product_id):
        if product_id in self.data.cart:
            del self.data.cart[product_id]
            self.save()

    def cart_lines(self):
        lines = []
        for product_id, quantity in self.data.cart.items():
            lines.append((self.data.products[product_id], quantity))
        return lines

    def cart_count(self):
        count = 0
        for quantity in self.data.cart.values():
            count += quantity
        return count

    def subtotal_cents(self):
        total = 0
        for product, quantity in self.cart_lines():
            total += product.price_cents * quantity
        return total

    def shipping_cents(self):
        subtotal = self.subtotal_cents()
        if subtotal == 0 or subtotal >= FREE_SHIPPING_MIN_CENTS:
            return 0
        return SHIPPING_CENTS

    def total_cents(self):
        return self.subtotal_cents() + self.shipping_cents()

    def checkout(self, now):
        if len(self.data.cart) == 0:
            raise EmptyCartError()

        for product, quantity in self.cart_lines():
            if quantity > product.stock:
                raise OutOfStockError(product.name, product.stock)

        lines = []
        for p, quantity in self.cart_lines():
            lines.append(OrderLine(p.id, p.name, p.image_file, p.price_cents, quantity))
        order = Order(f"ALB-{self.data.next_order_number}", now, lines,
                      self.subtotal_cents(), self.shipping_cents())

        for line in lines:
            self.data.products[line.product_id].reduce_stock(line.quantity)
        self.data.orders.append(order)
        self.data.next_order_number += 1
        self.data.cart.clear()
        self.save()
        return order

    def orders(self, status, now):
        results = []

        for order in reversed(self.data.orders):
            if status == "All" or order.status(now) == status:
                results.append(order)
        return results
