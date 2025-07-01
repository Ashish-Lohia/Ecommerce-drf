from django.urls import path
from .views import get_notifications, mark_notification_read, unread_notifications_count

urlpatterns = [
    path("notifications/", get_notifications, name="get_notifications"),
    path(
        "notifications/unread_count/",
        unread_notifications_count,
        name="unread_notifications_count",
    ),
    path(
        "notifications/<uuid:notification_id>/read/",
        mark_notification_read,
        name="mark_notification_read",
    ),
]
