from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from users.models import User
from product.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(UUID, TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    content = models.TextField()

    def __str__(self):
        return f"Review of {self.product.name} by {self.user.fullname}"

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "product")


class ReviewMedia(UUID, TimeStampModel):
    TYPE_CHOICES = (
        ("image", "Image"),
        ("video", "Video"),
    )

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="multimedia"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="image")
    url = models.URLField()

    def __str__(self):
        return f"Files of {self.review.id}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Review Media"
        verbose_name_plural = "Review Media"
