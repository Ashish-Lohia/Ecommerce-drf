from rest_framework import serializers
from delivery.models import Delivery


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DeliveryListSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="order.id", read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id",
            "order_id",
            "provider",
            "tracking_id",
            "status",
            "estimated_delivery_date",
            "created_at",
        ]
