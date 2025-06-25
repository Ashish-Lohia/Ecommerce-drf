from django.db import models
from users.models import User
from ecommerce.utils.models import UUID, TimeStampModel


class Address(UUID, TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    landmark = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Address of {self.user.fullname}"

    def get_full_address(self):
        parts = [
            self.address_line,
            self.landmark,
            self.city,
            self.state,
            self.country,
            self.pin_code,
        ]
        return ", ".join(filter(None, parts))

    class Meta:
        verbose_name_plural = "Addresses"
