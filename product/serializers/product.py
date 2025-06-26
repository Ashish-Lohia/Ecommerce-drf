from rest_framework import serializers
from product.models import Product
from product.serializers import BrandCategorySerializer
from .brand import BrandListSerializer
from .category import CategoryListSerializer
from .size import SizeSerializer
from users.serializers import UserProfileSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "owner"]


class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandListSerializer()
    category = CategoryListSerializer()
    size = SizeSerializer()
    owner = UserProfileSerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "stock",
            "brand",
            "category",
            "size",
            "is_archived",
            "owner",
            "created_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandListSerializer()
    category = CategoryListSerializer()
    size = SizeSerializer()
    owner = UserProfileSerializer()

    class Meta:
        model = Product
        fields = "__all__"
