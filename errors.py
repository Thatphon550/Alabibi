class StoreError(Exception):
    pass

class ProductNotFoundError(StoreError):
    def __init__(self, product_id):
        super().__init__(f"Product {product_id} does not exist")
        self.product_id = product_id

class OutOfStockError(StoreError):
    def __init__(self, product_name, available):
        if available == 0:
            message = f"{product_name} is out of stock"
        else:
            message = f"Only {available} {product_name} left in stock"
        super().__init__(message)
        self.product_name = product_name
        self.available = available

class EmptyCartError(StoreError):
    def __init__(self):
        super().__init__("Your cart is empty")
