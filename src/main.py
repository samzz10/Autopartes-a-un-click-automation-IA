# carito.py

class CartError(Exception):
    """Base para errores del carrito."""
    pass


class InvalidQuantityError(CartError):
    pass


class LimitExceededError(CartError):
    pass


class OutOfStockError(CartError):
    pass


MAX_PER_PRODUCT = 5  # límite por cliente


class Product:
    def __init__(self, sku: str, name: str, price: float, stock: int):
        self.sku = sku
        self.name = name
        self.price = float(price)
        self.stock = int(stock)

    def __repr__(self):
        return f"Product({self.sku}, {self.name}, {self.price}, stock={self.stock})"

    # Para usar como clave en dict
    def __hash__(self):
        return hash(self.sku)

    def __eq__(self, other):
        return isinstance(other, Product) and self.sku == other.sku


class Cart:
    def __init__(self):
        # mapa: product -> quantity
        self._items = {}

    def add(self, product: Product, quantity: int = 1):
        """Agrega 'quantity' unidades si cumple reglas."""
        if quantity <= 0:
            raise InvalidQuantityError("Cantidad debe ser >= 1.")

        current_qty = self._items.get(product, 0)

        if current_qty + quantity > MAX_PER_PRODUCT:
            raise LimitExceededError(f"Límite de {MAX_PER_PRODUCT} por producto.")

        if quantity > product.stock:
            raise OutOfStockError("Cantidad supera stock disponible.")

        # aplica cambios
        self._items[product] = current_qty + quantity
        product.stock -= quantity

        return self.subtotal()

    def qty_of(self, product: Product) -> int:
        return self._items.get(product, 0)

    def subtotal(self) -> float:
        return sum(prod.price * qty for prod, qty in self._items.items())
