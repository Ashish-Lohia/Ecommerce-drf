from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from .category import Category
from .brand import Brand
from .size import Size
from users.models import User


class Product(UUID, TimeStampModel):
    name = models.CharField(max_length=200)
    desp = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True,
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, related_name="products", null=True, blank=True
    )
    size = models.ForeignKey(
        Size, on_delete=models.SET_NULL, related_name="products", null=True, blank=True
    )
    is_archived = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return f"{self.name}-{self.owner.fullname}"

    class Meta:
        ordering = ["created_at", "name"]
