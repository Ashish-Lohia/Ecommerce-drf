import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from notification.models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")

        if self.user and not isinstance(self.user, AnonymousUser):
            self.group_name = f"user_{self.user.id}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)

            await self.accept()

            unread_count = await self.get_unread_count()
            await self.send(
                text_data=json.dumps({"type": "unread_count", "count": unread_count})
            )
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("type") == "mark_read":
            notification_id = data.get("notification_id")
            if notification_id:
                success = await self.mark_notification_read(notification_id)
                # Send confirmation back to client
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "mark_read_response",
                            "success": success,
                            "notification_id": notification_id,
                        }
                    )
                )

    async def send_notification(self, event):
        """Send notification to WebSocket"""
        notification = event["notification"]

        await self.send(
            text_data=json.dumps({"type": "notification", "data": notification})
        )

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
