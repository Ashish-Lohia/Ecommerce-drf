from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from notification.models import Notification
from django.db.models import Q


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """Get user notifications with pagination"""
    notifications_qs = Notification.objects.filter(user=request.user)
    unread_count = notifications_qs.filter(is_read=False).count()
    notifications = notifications_qs[:20]

    data = [
        {
            "id": str(n.id),
            "title": n.title,
            "message": n.message,
            "type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
            "data": n.data,
        }
        for n in notifications
    ]

    return Response(
        {
            "notifications": data,
            "unread_count": unread_count,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"status": "success"})
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_notifications_count(request):
    """Get unread notifications count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({"count": count})
