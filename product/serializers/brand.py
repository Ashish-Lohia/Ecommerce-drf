from rest_framework import serializers
from product.models import Brand
from .category import CategoryListSerializer


class BrandSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    sizes_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "logo",
            "website",
            "categories",
            "sizes_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_categories(self, obj):
        brand_categories = obj.brand_categories.all()
        categories = [bc.category for bc in brand_categories]
        return CategoryListSerializer(categories, many=True, context=self.context).data

    def get_sizes_count(self, obj):
        return obj.sizes.count()


class BrandListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing brands without nested categories"""

    categories_count = serializers.SerializerMethodField()
    sizes_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "logo",
            "website",
            "categories_count",
            "sizes_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_categories_count(self, obj):
        return obj.brand_categories.count()

    def get_sizes_count(self, obj):
        return obj.sizes.count()
