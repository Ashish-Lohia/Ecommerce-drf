from rest_framework import serializers
from cart.models import Cart, CartItem
from product.serializers import ProductListSerializer
from product.models import Product
from rest_framework.exceptions import ValidationError


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise ValidationError("Invalid product_id: Product does not exist.")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        validated_data["product"] = Product.objects.get(id=product_id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("product_id", None)
        return super().update(instance, validated_data)


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "owner",
            "cart_items",
            "total_items",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "total_items",
            "total_price",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return obj.get_total_items()

    def get_total_price(self, obj):
        return obj.get_total_price()
