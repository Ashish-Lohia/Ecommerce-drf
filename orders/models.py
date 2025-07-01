from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from users.models import User
from product.models import Product
from coupons.models import Coupon


class Order(UUID, TimeStampModel):
    STATUS_CHOICES = (
        ("created", "Created"),
        ("confirmed", "Confirmed"),
        ("pickup_scheduled", "Pickup Scheduled"),
        ("picked_up", "Picked Up"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="orders_bought",
        blank=True,
        null=True,
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="orders_sold",
        blank=True,
        null=True,
    )
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    convenience_fee = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupons = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, related_name="orders", blank=True, null=True
    )
    invoice = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="created")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order of {self.buyer.fullname} ({self.id})"

    def get_total_items(self):
        return sum(item.quantity for item in self.order_items.all())

    def get_total_price(self):
        return sum(
            item.quantity * item.product.price for item in self.order_items.all()
        )


class OrderItem(UUID, TimeStampModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, related_name="orders", null=True, blank=True
    )
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.id}"


class OrderStatusHistory(UUID, TimeStampModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history"
    )
    previous_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order.id}: {self.previous_status} -> {self.new_status}"

    class Meta:
        ordering = ["-created_at"]
