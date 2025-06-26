from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="order.id", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "order",
            "order_id",
            "provider",
            "provider_trxn_id",
            "status",
            "amount",
            "confirmed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
