import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from product.models import ProductMedia
from orders.models import Order, OrderStatusHistory
from coupons.models import CouponUser
from ecommerce.tasks import (
    process_product_media,
    send_order_notification_email,
    send_websocket_notification,
    update_coupon_usage_stats,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ProductMedia)
def trigger_media_processing(sender, instance, created, **kwargs):
    """Trigger media processing when new media is uploaded"""
    if created and instance.type == "image":
        try:
            process_product_media.delay(instance.id)
            logger.info(f"Media processing queued for ProductMedia {instance.id}")
        except Exception as e:
            logger.error(
                f"Failed to queue media processing for ProductMedia {instance.id}: {str(e)}"
            )


@receiver(post_save, sender=Order)
def handle_order_updates(sender, instance, created, **kwargs):
    """Handle order creation and status updates"""
    if created:
        # New order created
        if instance.seller:
            # Send email notification with error handling
            try:
                send_order_notification_email.delay(instance.id, "seller")
                logger.info(
                    f"Email notification queued for order {instance.id} to seller"
                )
            except Exception as e:
                logger.error(
                    f"Failed to queue email notification for order {instance.id} to seller: {str(e)}"
                )

            # Send WebSocket notification with error handling
            try:
                send_websocket_notification.delay(
                    instance.seller.id,
                    {
                        "title": "New Order Received!",
                        "message": f'Order #{instance.id} from {instance.buyer.fullname if instance.buyer else "Guest"}',
                        "notification_type": "order_new",
                        "data": {
                            "order_id": str(instance.id),
                            "buyer_name": (
                                instance.buyer.fullname if instance.buyer else "Guest"
                            ),
                            "total_amount": str(instance.total_amount),
                        },
                    },
                )
                logger.info(
                    f"WebSocket notification queued for order {instance.id} to seller"
                )
            except Exception as e:
                logger.error(
                    f"Failed to queue WebSocket notification for order {instance.id} to seller: {str(e)}"
                )
    else:
        # Order updated - check if status changed
        try:
            old_instance = Order.objects.get(id=instance.id)
            if hasattr(instance, "_state") and not instance._state.adding:
                # Status might have changed, notify buyer
                if instance.buyer:
                    # Send email notification with error handling
                    try:
                        send_order_notification_email.delay(instance.id, "buyer")
                        logger.info(
                            f"Email notification queued for order {instance.id} to buyer"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to queue email notification for order {instance.id} to buyer: {str(e)}"
                        )

                    # Send WebSocket notification with error handling
                    try:
                        send_websocket_notification.delay(
                            instance.buyer.id,
                            {
                                "title": "Order Status Updated",
                                "message": f"Your order #{instance.id} is now {instance.get_status_display()}",
                                "notification_type": "order_update",
                                "data": {
                                    "order_id": str(instance.id),
                                    "new_status": instance.status,
                                    "status_display": instance.get_status_display(),
                                },
                            },
                        )
                        logger.info(
                            f"WebSocket notification queued for order {instance.id} to buyer"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to queue WebSocket notification for order {instance.id} to buyer: {str(e)}"
                        )
        except Order.DoesNotExist:
            pass


@receiver(pre_save, sender=Order)
def track_order_status_changes(sender, instance, **kwargs):
    """Track order status changes"""
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Create status history record
                OrderStatusHistory.objects.create(
                    order=instance,
                    previous_status=old_instance.status,
                    new_status=instance.status,
                    # You can add changed_by if you track who made the change
                )
                logger.info(
                    f"Status change recorded for order {instance.id}: {old_instance.status} -> {instance.status}"
                )
        except Order.DoesNotExist:
            pass
        except Exception as e:
            logger.error(
                f"Failed to create status history for order {instance.id}: {str(e)}"
            )


@receiver(post_save, sender=CouponUser)
def update_coupon_stats_on_use(sender, instance, created, **kwargs):
    """Update coupon usage statistics when coupon is used"""
    if created:
        try:
            # Delay the update to avoid race conditions
            update_coupon_usage_stats.apply_async(countdown=5)
            logger.info(
                f"Coupon usage stats update queued for CouponUser {instance.id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to queue coupon usage stats update for CouponUser {instance.id}: {str(e)}"
            )
