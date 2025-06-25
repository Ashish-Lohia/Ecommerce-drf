from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from .category import Category
from .brand import Brand


class Size(UUID, TimeStampModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="sizes"
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="sizes")

    def __str__(self):
        return f"{self.name} ({self.brand.name} - {self.category.name})"

    class Meta:
        unique_together = ("category", "brand", "name")
        ordering = ["brand__name", "category__name", "name"]
