from django.db import models
from django.utils.text import slugify
from ecommerce.utils.models import UUID, TimeStampModel


class Category(UUID, TimeStampModel):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", blank=True, null=True
    )
    slug = models.SlugField(max_length=500, unique=True, blank=True)

    def __str__(self):
        return self.slug

    def get_ancestor_names(self):
        names = []
        current = self
        while current:
            names.insert(0, current.name)
            current = current.parent
        return names

    def save(self, *args, **kwargs):
        if not self.slug:
            full_path = "/".join([slugify(name) for name in self.get_ancestor_names()])
            self.slug = full_path
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "categories"
