from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from users.models import User


class Notification(UUID, TimeStampModel):
    NOTIFICATION_TYPES = [
        ("order_new", "New Order"),
        ("order_update", "Order Update"),
        ("coupon_expiry", "Coupon Expiry"),
        ("stock_alert", "Stock Alert"),
        ("payment_success", "Payment Success"),
        ("system", "System Notification"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default="system"
    )
    is_read = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
