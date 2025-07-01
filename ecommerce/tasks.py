from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.core.files.storage import default_storage
from PIL import Image
import requests
import os
import tempfile
from decimal import Decimal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from users.models import User
from product.models import Product, ProductMedia, ProcessedProductMedia
from orders.models import Order
from coupons.models import Coupon

from notification.models import Notification


@shared_task(bind=True)
def process_product_media(self, media_id):
    """Process product images/videos - resize, optimize, create thumbnails"""
    try:
        media = ProductMedia.objects.get(id=media_id)
        processed_media, created = ProcessedProductMedia.objects.get_or_create(
            original_media=media, defaults={"processing_status": "processing"}
        )

        if media.type == "image":
            # Download image from URL
            response = requests.get(media.url)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile() as temp_file:
                    temp_file.write(response.content)
                    temp_file.flush()

                    # Process image
                    with Image.open(temp_file.name) as img:
                        # Create main processed image (max 1200x1200)
                        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)

                        # Save processed image
                        processed_path = (
                            f"processed/products/{media.product.id}_{media.id}_main.jpg"
                        )
                        with tempfile.NamedTemporaryFile(
                            suffix=".jpg"
                        ) as processed_temp:
                            img.save(
                                processed_temp.name, "JPEG", quality=85, optimize=True
                            )
                            processed_temp.seek(0)

                            # Upload to storage (local or cloud)
                            saved_path = default_storage.save(
                                processed_path, processed_temp
                            )
                            processed_media.processed_url = default_storage.url(
                                saved_path
                            )

                        # Create thumbnail (300x300)
                        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                        thumbnail_path = f"processed/products/{media.product.id}_{media.id}_thumb.jpg"
                        with tempfile.NamedTemporaryFile(suffix=".jpg") as thumb_temp:
                            img.save(thumb_temp.name, "JPEG", quality=75, optimize=True)
                            thumb_temp.seek(0)

                            saved_thumb_path = default_storage.save(
                                thumbnail_path, thumb_temp
                            )
                            processed_media.thumbnail_url = default_storage.url(
                                saved_thumb_path
                            )

                        processed_media.processing_status = "completed"
                        processed_media.file_size = os.path.getsize(temp_file.name)
                        processed_media.save()

                        return f"Successfully processed image for product {media.product.name}"
            else:
                processed_media.processing_status = "failed"
                processed_media.save()
                return f"Failed to download image: {response.status_code}"

    except Exception as e:
        processed_media.processing_status = "failed"
        processed_media.save()
        self.retry(countdown=60, max_retries=3)
        return f"Error processing media: {str(e)}"


@shared_task
def deactivate_expired_coupons():
    """Deactivate expired coupons and notify admin"""
    try:
        expired_coupons = Coupon.objects.filter(
            valid_to__lt=timezone.now(), is_active=True
        )

        expired_codes = list(expired_coupons.values_list("code", flat=True))
        count = expired_coupons.update(is_active=False)

        if count > 0:
            # Notify admin
            admin_users = User.objects.filter(role__in=["admin", "superadmin"])
            for admin in admin_users:
                send_websocket_notification.delay(
                    admin.id,
                    {
                        "title": "Coupons Expired",
                        "message": f"{count} coupons have been deactivated",
                        "notification_type": "coupon_expiry",
                        "data": {"expired_codes": expired_codes},
                    },
                )

        return f"Deactivated {count} expired coupons: {expired_codes}"
    except Exception as e:
        return f"Error deactivating coupons: {str(e)}"


@shared_task
def send_order_notification_email(order_id, recipient_type):
    """Send order notification emails to buyer/seller"""
    try:
        order = Order.objects.select_related("buyer", "seller").get(id=order_id)
    except Order.DoesNotExist:
        return f"Error: Order with ID {order_id} does not exist."

    try:
        if recipient_type == "buyer" and order.buyer:
            user = order.buyer
            subject = f"Order Update - #{order.id}"
            message = f"""
                            Dear {user.fullname},

                            Your order status has been updated to: {order.get_status_display()}
                            Order ID: {order.id}
                            Total Amount: ₹{order.total_amount}

                            Track your order status in your account dashboard.

                            Best regards,
                            Your Ecommerce Team
                            """
        elif recipient_type == "seller" and order.seller:
            user = order.seller
            subject = f"New Order Received - #{order.id}"
            items_count = order.get_total_items()
            message = f"""
                            Dear {user.fullname},

                            You have received a new order!
                            Order ID: {order.id}
                            Buyer: {order.buyer.fullname if order.buyer else 'N/A'}
                            Items: {items_count}
                            Total Amount: ₹{order.total_amount}
                            Status: {order.get_status_display()}

                            Please login to your seller dashboard to manage this order.

                            Best regards,
                            Your Ecommerce Team
                            """
        else:
            return f"Invalid recipient type '{recipient_type}' or user not found for order {order.id}"

        send_mail(
            subject.strip(),
            message.strip(),
            "noreply@yourecommerce.com",
            [user.email],
            fail_silently=False,
        )

        return f"Email sent to {user.email} ({recipient_type})"
    except Exception as e:
        return f"Error sending email for order {order_id}: {str(e)}"


@shared_task
def send_websocket_notification(user_id, notification_data):
    """Send real-time notification via WebSocket and save to database"""
    try:
        if not User.objects.filter(id=user_id).exists():
            return f"Error: User with ID {user_id} does not exist."

        notification = Notification.objects.create(
            user_id=user_id,
            title=notification_data["title"],
            message=notification_data["message"],
            notification_type=notification_data.get("notification_type", "system"),
            data=notification_data.get("data", {}),
        )

        # Send via WebSocket
        channel_layer = get_channel_layer()
        group_name = f"user_{user_id}"

        # FIXED: Send notification data in the correct format
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification": {
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.notification_type,
                    "notification_type": notification.notification_type,
                    "data": notification.data,
                    "created_at": notification.created_at.isoformat(),
                    "is_read": notification.is_read,
                },
            },
        )

        return f"Notification sent to user {user_id}"
    except Exception as e:
        return f"Error sending notification to user {user_id}: {str(e)}"


@shared_task
def check_low_stock_products():
    """Check for products with low stock and notify sellers"""
    try:
        low_stock_threshold = Decimal("10.00")  # Adjust as needed
        low_stock_products = Product.objects.filter(
            stock__lte=low_stock_threshold, is_archived=False
        ).select_related("owner")

        notifications_sent = 0
        for product in low_stock_products:
            send_websocket_notification.delay(
                product.owner.id,
                {
                    "title": "Low Stock Alert",
                    "message": f'Your product "{product.name}" is running low on stock ({product.stock} remaining)',
                    "notification_type": "stock_alert",
                    "data": {
                        "product_id": str(product.id),
                        "current_stock": str(product.stock),
                        "threshold": str(low_stock_threshold),
                    },
                },
            )
            notifications_sent += 1

        return f"Sent {notifications_sent} low stock notifications"
    except Exception as e:
        return f"Error checking stock: {str(e)}"


@shared_task
def generate_sales_analytics():
    """Generate daily sales analytics and reports"""
    try:
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        # Daily statistics
        daily_orders = Order.objects.filter(created_at__date=today)
        yesterday_orders = Order.objects.filter(created_at__date=yesterday)

        analytics = {
            "date": today.isoformat(),
            "total_orders": daily_orders.count(),
            "completed_orders": daily_orders.filter(status="completed").count(),
            "total_revenue": sum(order.total_amount for order in daily_orders),
            "yesterday_orders": yesterday_orders.count(),
            "growth_rate": 0,
        }

        # Calculate growth rate
        if yesterday_orders.count() > 0:
            analytics["growth_rate"] = (
                (analytics["total_orders"] - analytics["yesterday_orders"])
                / analytics["yesterday_orders"]
                * 100
            )

        # Send report to admins
        admin_users = User.objects.filter(role__in=["admin", "superadmin"])
        for admin in admin_users:
            send_websocket_notification.delay(
                admin.id,
                {
                    "title": "Daily Sales Report",
                    "message": f'Daily analytics ready: {analytics["total_orders"]} orders, ₹{analytics["total_revenue"]} revenue',
                    "notification_type": "system",
                    "data": analytics,
                },
            )

        return f"Analytics generated for {today}: {analytics}"
    except Exception as e:
        return f"Error generating analytics: {str(e)}"


@shared_task
def cleanup_old_notifications():
    """Clean up old notifications (older than 30 days)"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        old_notifications = Notification.objects.filter(created_at__lt=cutoff_date)
        count = old_notifications.count()
        old_notifications.delete()

        return f"Deleted {count} old notifications"
    except Exception as e:
        return f"Error cleaning notifications: {str(e)}"


@shared_task
def update_coupon_usage_stats():
    """Update coupon usage statistics"""
    try:
        coupons = Coupon.objects.filter(is_active=True)
        updated_count = 0

        for coupon in coupons:
            old_count = coupon.used_count
            coupon.update_used_count()
            if coupon.used_count != old_count:
                updated_count += 1

        return f"Updated usage stats for {updated_count} coupons"
    except Exception as e:
        return f"Error updating coupon stats: {str(e)}"


@shared_task
def send_abandoned_cart_reminders():
    """Send reminders for abandoned carts (if you have cart functionality)"""
    # This would require a Cart model - placeholder implementation
    try:
        # You would implement cart abandonment logic here
        # For now, returning a placeholder
        return "Cart reminder functionality would be implemented here"
    except Exception as e:
        return f"Error with cart reminders: {str(e)}"


@shared_task
def process_bulk_product_updates():
    """Process bulk product updates (price changes, stock updates, etc.)"""
    try:
        # This could be triggered by admin actions or CSV uploads
        # Placeholder for bulk operations
        return "Bulk update functionality would be implemented here"
    except Exception as e:
        return f"Error with bulk updates: {str(e)}"
