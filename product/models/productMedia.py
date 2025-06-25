from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from .product import Product


class ProductMedia(UUID, TimeStampModel):
    TYPE_CHOICES = [("image", "Image"), ("video", "Video")]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    url = models.URLField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="multimedia"
    )

    def __str__(self):
        return f"{self.type} - {self.product.name}"

    class Meta:
        ordering = ["created_at", "product__name"]
