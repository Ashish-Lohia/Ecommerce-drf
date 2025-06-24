from django.db import models
from django.conf import settings
from ecommerce.utils.models import UUID, TimeStampModel


class Category(UUID, TimeStampModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Size(UUID, TimeStampModel):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Brand(UUID, TimeStampModel):
    name = models.CharField(max_length=50, unique=True)
    logo = models.URLField()

    def __str__(self):
        return self.name


class Product(UUID, TimeStampModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    isArchived = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.id}, ({self.name})"


class ProductImage(UUID, TimeStampModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.URLField()

    def __str__(self):
        return self.image_url
