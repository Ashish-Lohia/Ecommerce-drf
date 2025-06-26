from rest_framework import serializers
from orders.models import Order, OrderItem
from product.serializers import ProductListSerializer
from coupons.serializers import CouponSerializer
from users.serializers import UserProfileSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "price_at_order", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, write_only=True)
    items = OrderItemSerializer(source="order_items", many=True, read_only=True)
    buyer = UserProfileSerializer(read_only=True)
    seller = UserProfileSerializer(read_only=True)
    coupons = CouponSerializer(read_only=True)
    coupons_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "buyer",
            "seller",
            "base_amount",
            "convenience_fee",
            "delivery_fee",
            "discount",
            "total_amount",
            "status",
            "completed_at",
            "coupons",
            "coupons_id",
            "invoice",
            "order_items",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "status"]

    def create(self, validated_data):
        items_data = validated_data.pop("order_items", [])
        coupon_id = validated_data.pop("coupons_id", None)

        if coupon_id:
            validated_data["coupons_id"] = coupon_id

        order = Order.objects.create(**validated_data)

        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                price_at_order=item["price_at_order"],
                quantity=item["quantity"],
            )
        return order
