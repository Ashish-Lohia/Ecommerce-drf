from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from orders.models import Order


class Transaction(UUID, TimeStampModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )

    PROVIDER_CHOICES = (
        ("razorpay", "Razorpay"),
        ("stripe", "Stripe"),
    )

    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, related_name="payment", blank=True, null=True
    )
    provider = models.CharField(
        max_length=50, choices=PROVIDER_CHOICES, default="razorpay"
    )
    provider_trxn_id = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.provider} | {self.status} | ₹{self.amount}"

    class Meta:
        ordering = ["-created_at"]
