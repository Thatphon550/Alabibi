from tkinter import *
from models import format_price

ORANGE = "#F4A26B"
BG = "#F2F2F2"
WHITE = "#FFFFFF"
GREY = "#777777"


class ScrollFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.canvas = Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = Scrollbar(self, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self.update_scroll_area)
        self.canvas.bind("<Configure>", self.update_width)

    def update_scroll_area(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_width(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def scroll(self, delta):
        if delta > 0:
            self.canvas.yview_scroll(-2, "units")
        else:
            self.canvas.yview_scroll(2, "units")

    def clear(self):
        for widget in self.inner.winfo_children():
            widget.destroy()
        self.canvas.yview_moveto(0)

class OptionButton(Button):
    def __init__(self, parent, text, value, on_click):
        super().__init__(parent, text=text, command=self.clicked)
        self.value = value
        self.on_click = on_click

    def clicked(self):
        self.on_click(self.value)

class ProductCard(Frame):
    def __init__(self, parent, app, product):
        super().__init__(parent, bg=WHITE, padx=10, pady=10, relief="solid", bd=1)
        self.app = app
        self.product = product

        Label(self, image=app.get_image(product.image_file), bg=WHITE).pack()
        Label(self, text=product.name, bg=WHITE, font=("Arial", 10, "bold")).pack()

        price = format_price(product.price_cents)
        if product.is_deal():
            price = price + " (was " + format_price(product.old_price_cents)  + ")"
        Label(self, text=price, bg=WHITE).pack()
        Label(self, text=product.stock_label(), bg=WHITE, fg=GREY).pack()

        buttons = Frame(self, bg=WHITE)
        buttons.pack(pady=(5, 0))
        Button(buttons, text="Details", command=self.show_details).pack(side="left", padx=2)
        add_button = Button(buttons, text="Add to Cart", bg=ORANGE, command=self.add)
        add_button.pack(side="left", padx=2)
        if not product.in_stock():
            add_button.configure(state="disabled")

    def add(self):
        self.app.add_to_cart(self.product.id)

    def show_details(self):
        self.app.show_product_details(self.product)

class CartRow(Frame):
    def __init__(self, parent, app, product, quantity):
        super().__init__(parent, bg=WHITE, padx=10, pady=5, relief="solid", bd=1)
        self.app = app
        self.product = product
        self.quantity = quantity

        Label(self, image=app.get_image(product.image_file, small=True), bg=WHITE).pack(side="left")
        text = product.name + "\n" + format_price(product.price_cents)
        Label(self, text=text, bg=WHITE, width=20, anchor="w", justify="left").pack(side="left", padx=10)

        Button(self, text="-", width=3, command=self.decrease).pack(side="left")
        Label(self, text=str(quantity), bg=WHITE, width=4).pack(side="left")
        Button(self, text="+", width=3, command=self.increase).pack(side="left")

        Button(self, text="Remove", command=self.remove).pack(side="right")
        line_total = format_price(product.price_cents * quantity)
        Label(self, text=line_total, bg=WHITE, width=10).pack(side="right")

    def decrease(self):
        self.app.change_quantity(self.product.id, self.quantity - 1)

    def increase(self):
        self.app.change_quantity(self.product.id, self.quantity + 1)

    def remove(self):
        self.app.remove_from_cart(self.product.id)

class OrderRow(Frame):
    def __init__(self, parent, app, order, now):
        super().__init__(parent, bg=WHITE, padx=10, pady=8, relief="solid", bd=1)
        self.app = app
        self.order = order
        self.now = now

        text = str(order) + "\nPlaced " + order.placed_at.strftime("%d %b %Y")

        Label(self, text=text, bg=WHITE, width=22, anchor="w", justify="left").pack(side="left")
        for line in order.lines:
            Label(self, image=app.get_image(line.image_file, small=True), bg=WHITE).pack(side="left")

        Button(self, text="Details", command=self.show_details).pack(side="right")
        Label(self, text=format_price(order.total_cents()), bg=WHITE, width=10).pack(side="right")
        Label(self, text=order.status(now), bg=WHITE, width=12).pack(side="right")

    def show_details(self):
        self.app.show_order_details(self.order)
