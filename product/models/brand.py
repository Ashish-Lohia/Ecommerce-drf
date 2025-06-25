from ecommerce.utils.models import UUID, TimeStampModel
from django.db import models


class Brand(UUID, TimeStampModel):
    name = models.CharField(max_length=50, unique=True)
    logo = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
