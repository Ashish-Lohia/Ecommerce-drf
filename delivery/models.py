from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from orders.models import Order


class Delivery(UUID, TimeStampModel):
    PROVIDER_CHOICES = (
        ("delhivery", "Delhivery"),
        ("xpressbees", "Xpressbees"),
    )

    STATUS_CHOICES = (
        ("pickup_scheduled", "Pickup Scheduled"),
        ("picked_up", "Picked Up"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, related_name="delivery", blank=True, null=True
    )
    provider = models.CharField(
        max_length=50, choices=PROVIDER_CHOICES, default="delhivery"
    )
    tracking_id = models.CharField(max_length=100, blank=True, null=True)
    tracking_website = models.URLField(default="https://www.delhivery.com/")
    shipping_label = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="pickup_scheduled"
    )
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.provider} | {self.tracking_id or 'N/A'} | {self.status}"

    class Meta:
        verbose_name_plural = "Deliveries"
        ordering = ["-created_at"]
