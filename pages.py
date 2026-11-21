from tkinter import *
from datetime import datetime

from models import format_price
from widgets import BG, ORANGE, CartRow, OptionButton, OrderRow, ProductCard, ScrollFrame


class Page(Frame):
    def __init__(self, parent, app, title):
        super().__init__(parent, bg=BG, padx=20, pady=15)
        self.app = app
        self.title_label = Label(self, text=title, bg=BG, font=("Arial", 18, "bold"))
        self.title_label.pack(anchor="w", pady=(0, 10))

    def refresh(self):
        raise NotImplementedError("Each page must have its own refresh()")

    def scroll(self, delta):
        pass

class ProductListPage(Page):
    COLUMNS = 4

    def __init__(self, parent, app, title):
        super().__init__(parent, app, title)
        self.top = Frame(self, bg=BG)
        self.top.pack(fill="x")
        self.grid_area = ScrollFrame(self)
        self.grid_area.pack(fill="both", expand=True)

    def get_products(self):
        raise NotImplementedError("Each product page must have its own get_products()")

    def refresh(self):
        self.grid_area.clear()
        products = self.get_products()
        if len(products) == 0:
            Label(self.grid_area.inner, text="No products found.", bg=BG).pack(anchor="w")
            return
        for i in range(len(products)):
            card = ProductCard(self.grid_area.inner, self.app, products[i])
            card.grid(row=i // self.COLUMNS, column =i % self.COLUMNS, padx=8, pady=8)

    def scroll(self, delta):
        self.grid_area.scroll(delta)

class HomePage(ProductListPage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Popular Products")

    def get_products(self):
        return self.app.store.all_products()

class DealsPage(ProductListPage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Deals / Clearance")

    def get_products(self):
        return self.app.store.deals()

class CategoriesPage(ProductListPage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Categories")
        self.category = app.store.categories()[0]
        for name in app.store.categories():
            OptionButton(self.top, name, name, self.choose).pack(side="left", padx=(0, 5), pady=(0, 10))

    def choose(self, category):
        self.category = category
        self.refresh()

    def get_products(self):
        return self.app.store.by_category(self.category)

    def refresh(self):
        self.title_label.configure(text="Categories: " + self.category)
        super().refresh()

class SearchPage(ProductListPage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Search")
        self.query = ""

    def get_products(self):
        return self.app.store.search(self.query)

    def refresh(self):
        self.title_label.configure(text='Results for "' + self.query + '"')
        super().refresh()

class CartPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Your Cart")
        self.rows = Frame(self, bg=BG)
        self.rows.pack(fill="x")

        summary = Frame(self, bg=BG)
        summary.pack(anchor="e", pady=15)
        self.summary_label = Label(summary, bg=BG, justify="right", font=("Arial", 11))
        self.summary_label.pack(anchor="e")
        self.checkout_button = Button(summary, text="Checkout", bg=ORANGE,
                                      width=15, command=app.checkout)
        self.checkout_button.pack(anchor="e", pady=5)
        Label(summary, text="Free shipping on orders over $50", bg=BG).pack(anchor="e")

    def refresh(self):
        for widget in self.rows.winfo_children():
            widget.destroy()

        store = self.app.store
        if store.cart_count() == 0:
            Label(self.rows, text="Your cart is empty.", bg=BG).pack(anchor="w")
            self.checkout_button.configure(state="disabled")
        else:
            self.checkout_button.configure(state="normal")
        for product, quantity in store.cart_lines():
            CartRow(self.rows, self.app, product, quantity).pack(fill="x", pady=3)

        if store.shipping_cents() == 0:
            shipping = "Free"
        else:
            shipping = format_price(store.shipping_cents())
        text = "Subtotal: " + format_price(store.subtotal_cents()) + "\n"
        text = text + "Shipping: " + shipping + "\n"
        text = text + "Total: " + format_price(store.total_cents())
        self.summary_label.configure(text=text)

class OrdersPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Your Orders")
        self.status = "All"
        filters = Frame(self, bg=BG)
        filters.pack(anchor="w", pady=(0, 10))
        for status in ["All", "Processing", "Shipped", "Delivered"]:
            OptionButton(filters, status, status, self.choose).pack(side="left", padx=(0, 5))
        self.list_area = ScrollFrame(self)
        self.list_area.pack(fill="both", expand=True)

    def choose(self, status):
        self.status = status
        self.refresh()

    def refresh(self):
        self.list_area.clear()
        now = datetime.now()
        orders = self.app.store.orders(self.status, now)
        if len(orders) == 0:
            Label(self.list_area.inner, text="No orders here.", bg=BG).pack(fill="x", pady=3)
        for order in orders:
            OrderRow(self.list_area.inner, self.app, order, now).pack(fill="x", pady=3)

    def scroll(self, delta):
        self.list_area.scroll(delta)


class SupportPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Customer Service")
        text = ("Need help with an order? Contact us:\n\n"
                "Email: help@alabibi.com\n"
                "Phone: 06-271-1488\n"
                "Open: Mon - Fri, 9:00 - 18:00\n\n"
                "Shipping is free on orders over $50.\n"
                "Orders ship within 1 day and arrive in about 3 days.")
        Label(self, text=text, bg=BG, justify="left", font=("Arial", 11)).pack(anchor="w")

    def refresh(self):
        pass
