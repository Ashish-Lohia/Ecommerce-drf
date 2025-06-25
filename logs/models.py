from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ecommerce.utils.models import UUID, TimeStampModel


class Logs(UUID, TimeStampModel):
    ACTION_TYPE_CHOICES = (
        ("info", "Info"),
        ("update", "Update"),
        ("status_change", "Status Change"),
        ("delete", "Delete"),
        ("create", "Create"),
        ("error", "Error"),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    message = models.TextField()
    data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"[{self.action_type.upper()}] {self.message[:50]}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Log"
        verbose_name_plural = "Logs"
