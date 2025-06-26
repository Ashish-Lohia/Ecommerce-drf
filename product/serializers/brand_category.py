from rest_framework import serializers
from product.models import BrandCategory
from .category import CategoryListSerializer
from .brand import BrandListSerializer


class BrandCategorySerializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source="brand.name")
    category_name = serializers.ReadOnlyField(source="category.name")
    category_slug = serializers.ReadOnlyField(source="category.slug")

    class Meta:
        model = BrandCategory
        fields = [
            "id",
            "brand",
            "category",
            "brand_name",
            "category_name",
            "category_slug",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class BrandCategoryDetailSerializer(serializers.ModelSerializer):
    brand = BrandListSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)

    class Meta:
        model = BrandCategory
        fields = ["id", "brand", "category", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
