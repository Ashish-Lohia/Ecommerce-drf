from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel
from users.models import User


class Coupon(UUID, TimeStampModel):
    TYPE_CHOICES = (
        ("percentage", "Percentage"),
        ("flat", "Flat"),
    )

    code = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=20, default="flat", choices=TYPE_CHOICES)
    max_value = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_use = models.PositiveIntegerField(default=1000000000)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code}"

    def update_used_count(self):
        self.used_count = self.users.count()
        self.save()

    class Meta:
        ordering = ["-created_at"]


class CouponUser(UUID):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="users")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="used_coupons"
    )
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coupon {self.coupon.code} used by {self.user.fullname}"

    class Meta:
        ordering = ["-used_at"]
