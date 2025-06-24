from rest_framework import serializers
from .models import ProductImage, Product, Category, Size, Brand


class CreateProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image_url"]


class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class CreateSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["name"]


class CreateBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "logo"]


class CreateProductSerializer(serializers.ModelSerializer):
    images = CreateProductImageSerializer(many=True, write_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "stock",
            "isArchived",
            "category",
            "size",
            "brand",
            "images",
        ]

    def validate_images(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("A maximum of 10 images are allowed.")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        return product
