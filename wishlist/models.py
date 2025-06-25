from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from users.models import User
from product.models import Product


class Wishlist(UUID, TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")

    def __str__(self):
        return f"Wishlist of {self.user.fullname}"

    def get_total_items(self):
        return self.products.count()


class WishlistItem(UUID, TimeStampModel):
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlist_items"
    )

    def __str__(self):
        return f"{self.wishlist.user.fullname} | {self.product.name}"

    class Meta:
        unique_together = ("wishlist", "product")
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
