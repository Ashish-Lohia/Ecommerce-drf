from rest_framework import serializers
from product.models import Size, BrandCategory
from .brand import BrandListSerializer
from .category import CategoryListSerializer


class SizeSerializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source="brand.name")
    category_name = serializers.ReadOnlyField(source="category.name")
    category_slug = serializers.ReadOnlyField(source="category.slug")

    class Meta:
        model = Size
        fields = [
            "id",
            "name",
            "brand",
            "category",
            "brand_name",
            "category_name",
            "category_slug",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        """Validate that the brand-category combination exists"""
        brand = data.get("brand")
        category = data.get("category")

        if brand and category:
            if not BrandCategory.objects.filter(
                brand=brand, category=category
            ).exists():
                raise serializers.ValidationError(
                    "The specified brand and category combination does not exist. "
                    "Please ensure the brand is associated with the category first."
                )
        return data


class SizeDetailSerializer(serializers.ModelSerializer):
    brand = BrandListSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)

    class Meta:
        model = Size
        fields = ["id", "name", "brand", "category", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class SizeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing sizes"""

    brand_name = serializers.ReadOnlyField(source="brand.name")
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Size
        fields = [
            "id",
            "name",
            "brand_name",
            "category_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
