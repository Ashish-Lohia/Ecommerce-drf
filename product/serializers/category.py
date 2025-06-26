from rest_framework import serializers
from product.models import Brand, Category, BrandCategory


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    ancestor_names = serializers.ReadOnlyField(source="get_ancestor_names")
    sizes_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "parent",
            "slug",
            "children",
            "ancestor_names",
            "sizes_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(
                obj.children.all(), many=True, context=self.context
            ).data
        return []

    def get_sizes_count(self, obj):
        return obj.sizes.count()


class CategoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing categories without nested children"""

    ancestor_names = serializers.ReadOnlyField(source="get_ancestor_names")
    children_count = serializers.SerializerMethodField()
    sizes_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "parent",
            "slug",
            "ancestor_names",
            "children_count",
            "sizes_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_children_count(self, obj):
        return obj.children.count()

    def get_sizes_count(self, obj):
        return obj.sizes.count()
