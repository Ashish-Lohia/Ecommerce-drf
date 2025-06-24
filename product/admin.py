from django.contrib import admin
from .models import Product, Category, Brand, Size, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "name",
        "price",
        "category",
        "brand",
        "isArchived",
        "created_at",
    )
    list_filter = ("owner", "category", "brand", "size", "isArchived")
    search_fields = ("id", "name", "owner")
    ordering = ("created_at",)
    inlines = [ProductImageInline]

    fieldsets = (
        ("Basic details", {"fields": ("name", "description", "owner")}),
        ("Stats", {"fields": ("price", "stock")}),
        ("Sub-Fields", {"fields": ("category", "size", "brand")}),
        ("Status", {"fields": ("isArchived",)}),
    )

    add_fieldsets = (
        (
            "Create Product",
            {
                "fields": (
                    "name",
                    "description",
                    "price",
                    "stock",
                    "owner",
                    "category",
                    "size",
                    "brand",
                ),
            },
        ),
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
    )
    search_fields = (
        "id",
        "name",
    )
    ordering = ("created_at",)
    fieldsets = (
        (
            "Category Details",
            {
                "fields": ("name",),
            },
        ),
    )


class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
    )
    search_fields = (
        "id",
        "name",
    )
    ordering = ("created_at",)
    fieldsets = (
        (
            "Category Details",
            {
                "fields": ("name", "logo"),
            },
        ),
    )


class SizeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
    )
    search_fields = (
        "id",
        "name",
    )
    ordering = ("created_at",)
    fieldsets = (
        (
            "Category Details",
            {
                "fields": ("name",),
            },
        ),
    )


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product__owner", "image_url", "created_at")
    search_fields = ("id", "product")


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Size, SizeAdmin)
