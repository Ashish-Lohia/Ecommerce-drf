from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from users.models import User
from orders.models import Order


class Dispute(UUID, TimeStampModel):
    STATUS_CHOICES = (
        ("created", "Created"),
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="disputes")
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="dispute"
    )
    content = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="created")
    result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Dispute raised by {self.user.fullname} on {self.order.id}"

    class Meta:
        ordering = ["-created_at"]


class DisputeMedia(UUID, TimeStampModel):
    TYPE_CHOICES = (
        ("image", "Image"),
        ("video", "Video"),
    )

    dispute = models.ForeignKey(
        Dispute, on_delete=models.CASCADE, related_name="multimedia"
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="image")
    url = models.URLField()

    def __str__(self):
        return f"File of dispute {self.dispute.id}"
