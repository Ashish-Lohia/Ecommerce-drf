from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from .productMedia import ProductMedia


class ProcessedProductMedia(UUID, TimeStampModel):
    original_media = models.OneToOneField(
        ProductMedia, on_delete=models.CASCADE, related_name="processed_version"
    )
    processed_url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    file_size = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Processed {self.original_media.type} for {self.original_media.product.name}"
