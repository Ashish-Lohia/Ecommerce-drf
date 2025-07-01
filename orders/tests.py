from unittest.mock import patch, MagicMock
from django.test import TestCase
from users.models import User
from orders.models import Order


class OrderSignalTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            fullname="seller", email="seller@example.com", password="testpass123"
        )
        self.buyer = User.objects.create_user(
            fullname="buyer", email="buyer@example.com", password="testpass123"
        )

    @patch("ecommerce.signals.send_websocket_notification.delay")
    @patch("ecommerce.signals.send_order_notification_email.delay")
    def test_order_creation_continues_despite_email_failure(
        self, mock_email, mock_websocket
    ):
        """Test that WebSocket notification still works if email fails."""

        # Mock email to raise exception
        mock_email.side_effect = Exception("Email service down")

        # Mock WebSocket to succeed
        mock_websocket.return_value = MagicMock()

        # Create order - this should succeed despite email failure
        order = Order.objects.create(
            seller=self.seller,
            buyer=self.buyer,
            total_amount=100.00,
            base_amount=90.00,
            convenience_fee=5.00,
            delivery_fee=5.00,
            status="created",
        )

        # Verify order was created successfully
        self.assertIsNotNone(order.id)
        self.assertEqual(order.status, "created")

        # Verify email was attempted
        mock_email.assert_called_once_with(order.id, "seller")

        # Verify WebSocket notification was still called despite email failure
        mock_websocket.assert_called_once()

        # Verify the WebSocket call has correct parameters
        call_args = mock_websocket.call_args[0]
        self.assertEqual(call_args[0], self.seller.id)  # seller ID

        # Check the notification structure matches what's sent in the signal
        notification_data = call_args[1]
        self.assertEqual(notification_data["notification_type"], "order_new")
        self.assertEqual(notification_data["title"], "New Order Received!")
        self.assertIn(str(order.id), notification_data["message"])
        self.assertEqual(notification_data["data"]["order_id"], str(order.id))
        self.assertEqual(notification_data["data"]["buyer_name"], self.buyer.fullname)
        self.assertEqual(
            notification_data["data"]["total_amount"], str(order.total_amount)
        )

    @patch("ecommerce.signals.send_websocket_notification.delay")
    @patch("ecommerce.signals.send_order_notification_email.delay")
    def test_both_notifications_work_normally(self, mock_email, mock_websocket):
        """Test that both notifications work when services are up."""

        # Mock both to succeed
        mock_email.return_value = MagicMock()
        mock_websocket.return_value = MagicMock()

        # Create order
        order = Order.objects.create(
            seller=self.seller,
            buyer=self.buyer,
            total_amount=100.00,
            base_amount=90.00,
            convenience_fee=5.00,
            delivery_fee=5.00,
            status="created",
        )

        # Verify both notifications were called
        mock_email.assert_called_once_with(order.id, "seller")
        mock_websocket.assert_called_once()

        # Verify order creation succeeded
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.status, "created")

        # Verify WebSocket notification structure
        call_args = mock_websocket.call_args[0]
        notification_data = call_args[1]
        self.assertEqual(notification_data["notification_type"], "order_new")
        self.assertEqual(notification_data["title"], "New Order Received!")

    @patch("ecommerce.signals.send_websocket_notification.delay")
    @patch("ecommerce.signals.send_order_notification_email.delay")
    def test_order_status_update_notifications(self, mock_email, mock_websocket):
        """Test that order status update notifications work correctly."""

        # Mock both to succeed
        mock_email.return_value = MagicMock()
        mock_websocket.return_value = MagicMock()

        # Create order first
        order = Order.objects.create(
            seller=self.seller,
            buyer=self.buyer,
            total_amount=100.00,
            base_amount=90.00,
            convenience_fee=5.00,
            delivery_fee=5.00,
            status="created",
        )

        # Reset mocks after creation
        mock_email.reset_mock()
        mock_websocket.reset_mock()

        # Update order status
        order.status = "processing"
        order.save()

        # Verify buyer was notified about status change
        mock_email.assert_called_once_with(order.id, "buyer")
        mock_websocket.assert_called_once()

        # Verify WebSocket notification for status update
        call_args = mock_websocket.call_args[0]
        self.assertEqual(call_args[0], self.buyer.id)  # buyer ID

        notification_data = call_args[1]
        self.assertEqual(notification_data["notification_type"], "order_update")
        self.assertEqual(notification_data["title"], "Order Status Updated")
        self.assertIn("processing", notification_data["message"].lower())
        self.assertEqual(notification_data["data"]["order_id"], str(order.id))
        self.assertEqual(notification_data["data"]["new_status"], "processing")
