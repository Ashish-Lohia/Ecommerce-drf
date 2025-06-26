from rest_framework import serializers
from .models import Review, ReviewMedia


class ReviewMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewMedia
        fields = ["id", "review", "type", "url", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ReviewSerializer(serializers.ModelSerializer):
    multimedia = ReviewMediaSerializer(many=True, read_only=True)
    user_name = serializers.ReadOnlyField(source="user.fullname")
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "rating",
            "content",
            "multimedia",
            "user_name",
            "product_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
