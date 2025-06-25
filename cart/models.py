from django.db import models
from users.models import User
from ecommerce.utils.models import UUID, TimeStampModel
from product.models import Product


class Cart(UUID, TimeStampModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")

    def __str__(self):
        return f"Cart of {self.owner.fullname} ({self.id})"

    def get_total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

    def get_total_price(self):
        return sum(item.quantity * item.product.price for item in self.cart_items.all())


class CartItem(UUID, TimeStampModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.id}"
