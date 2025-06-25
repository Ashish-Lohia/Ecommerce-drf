from rest_framework import serializers
from .models import ProductMedia, Product, Category, Size, Brand, BrandCategory


class CreateProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ["type", "url"]


class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "parent"]


class CreateSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["name", "category", "brand"]


class CreateBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "logo", "website"]


class CreateProductSerializer(serializers.ModelSerializer):
    multimedia = CreateProductMediaSerializer(many=True, write_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "desp",
            "price",
            "stock",
            "is_archived",
            "category",
            "size",
            "brand",
            "multimedia",
        ]

    def validate_multimedia(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("A maximum of 10 files are allowed.")
        return value

    def create(self, validated_data):
        multimedia_data = validated_data.pop("multimedia", [])
        product = Product.objects.create(**validated_data)
        for url in multimedia_data:
            ProductMedia.objects.create(product=product, **url)
        return product
