from notification.models import Notification


def send_notification(user, title, message, notification_type="system", data=None):
    if data is None:
        data = {}
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        data=data,
    )
