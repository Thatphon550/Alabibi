from tkinter import *
from datetime import datetime
from tkinter import messagebox

from errors import StoreError
from models import format_price
from pages import CartPage, CategoriesPage, DealsPage, HomePage, OrdersPage, SearchPage, SupportPage
from store import Store
from widgets import BG, ORANGE, OptionButton

class App(Tk):
    def __init__(self, data_path, image_folder):
        super().__init__()
        self.title("Alabibi Online Store")
        self.geometry("1150x720")
        self.configure(bg=BG)

        self.store = Store(data_path)
        self.image_folder = image_folder
        self.images = {}

        self.current = "home"

        self.make_sidebar()
        self.make_top_bar()

        content = Frame(self, bg=BG)
        content.pack(side="top", fill="both", expand=True)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.pages["home"] = HomePage(content, self)
        self.pages["categories"] = CategoriesPage(content, self)
        self.pages["deals"] = DealsPage(content, self)
        self.pages["search"] = SearchPage(content, self)
        self.pages["cart"] = CartPage(content, self)
        self.pages["orders"] = OrdersPage(content, self)
        self.pages["support"] = SupportPage(content, self)
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_page("home")

    def make_sidebar(self):
        sidebar = Frame(self, bg=ORANGE, width=200, padx=15, pady=15)
        sidebar.pack(side="left", fill="y")
        Label(sidebar, text="Alabibi", bg=ORANGE, fg="white",
              font=("Arial", 24, "bold")).pack(pady=(0, 20))

        links = [("Home", "home"), ("Categories", "categories"), ("Deals / Clearance", "deals"),
                 ("Your Cart", "cart"), ("Your Orders", "orders"), ("Customer Service", "support")]
        for text, page_name in links:
            button = OptionButton(sidebar, text, page_name, self.show_page)
            button.configure(width=18, anchor="w")
            button.pack(pady=3)

        Label(sidebar, text="User", bg=ORANGE, fg="white", font=("Arial", 12)).pack(side="bottom")

    def make_top_bar(self):
        top = Frame(self, bg="#E6E6E6", padx=15, pady=10)
        top.pack(side="top", fill="x")

        self.search_entry = Entry(top, width=40, font=("Arial", 11))
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", self.on_enter)
        Button(top, text="Search", command=self.search).pack(side="left", padx=5)
        Button(top, text="X", command=self.clear_search).pack(side="left")

        self.cart_button = Button(top, text="Cart (0)", command=self.open_cart)
        self.cart_button.pack(side="right", padx=5)
        bell = self.get_image("bell_dark.png", folder="icons")
        Button(top, image=bell, command=self.show_notifications).pack(side="right")

    def get_image(self, filename, small=False, folder="products"):
        key = folder + "/" + filename + str(small)
        if key not in self.images:
            try:
                image = PhotoImage(file=str(self.image_folder / folder / filename))
            except TclError:
                image = PhotoImage(file=str(self.image_folder / "products" / "placeholder.png"))
            if small:
                image = image.subsample(2)
            self.images[key] = image
        return self.images[key]

    def show_page(self, name):
        self.current = name
        page = self.pages[name]
        page.refresh()
        page.tkraise()
        self.cart_button.configure(text="Cart (" + str(self.store.cart_count()) + ")")

    def refresh(self):
        self.show_page(self.current)

    def open_cart(self):
        self.show_page("cart")

    def add_to_cart(self, product_id):
        try:
            self.store.add_to_cart(product_id)
        except StoreError as error:
            messagebox.showerror("Sorry", str(error))
            return
        product = self.store.get_product(product_id)
        messagebox.showinfo("Added to cart", product.name + " was added to your cart.")
        self.refresh()

    def change_quantity(self, product_id, quantity):
        try:
            self.store.set_quantity(product_id, quantity)
        except StoreError as error:
            messagebox.showerror("Sorry", str(error))
        self.refresh()

    def remove_from_cart(self, product_id):
        self.store.remove_from_cart(product_id)
        self.refresh()

    def checkout(self):
        total = format_price(self.store.total_cents())
        if not messagebox.askyesno("Checkout", "Place your order for " + total + "?"):
            return
        try:
            order = self.store.checkout(datetime.now())
        except StoreError as error:
            messagebox.showerror("Sorry", str(error))
            return
        messagebox.showinfo("Thank you!", "Your order " + order.order_id + " has been placed.")
        self.show_page("orders")

    def show_product_details(self, product):
        text = product.name + "\n" + format_price(product.price_cents) + "\n"
        text = text + "Category: " + product.category + "\n"

        for line in product.details():
            text = text + line + "\n"
        text = text + product.stock_label()
        messagebox.showinfo(product.name, text)

    def show_order_details(self, order):
        text = "Placed " + order.placed_at.strftime("%d %b %Y %H:%M") + "\n"
        text = text + "Status: " + order.status(datetime.now()) + "\n\n"
        for line in order.lines:
            text = text + line.name + " x" + str(line.quantity) + "   "
            text = text + format_price(line.line_total_cents()) + "\n"
        text = text + "\nTotal: " + format_price(order.total_cents())
        messagebox.showinfo(str(order), text)

    def on_enter(self, event):
        self.search()

    def search(self):
        query = self.search_entry.get().strip()
        if query == "":
            return
        self.pages["search"].query = query
        self.show_page("search")

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.show_page("home")

    def show_notifications(self):
        now = datetime.now()
        text = ""
        for order in self.store.orders("All", now):
            text = text + str(order) + " is " + order.status(now).lower() + "\n"

        if text == "":
            text = "No notifications."
        messagebox.showinfo("Notifications", text)

    def on_mouse_wheel(self, event):
        self.pages[self.current].scroll(event.delta)

    def on_close(self):
        self.store.save()
        self.destroy()
