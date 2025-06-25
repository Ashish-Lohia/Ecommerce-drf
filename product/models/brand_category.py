from ecommerce.utils.models import UUID, TimeStampModel
from django.db import models
from .category import Category
from .brand import Brand


class BrandCategory(UUID, TimeStampModel):
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="brand_categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category_brands"
    )

    def __str__(self):
        return f"{self.brand.name}-{self.category.name}"

    class Meta:
        ordering = ["brand__name", "category__name"]
        verbose_name = "Brand_Category_Pair"
        unique_together = ("brand", "category")
