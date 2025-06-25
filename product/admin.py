from django.contrib import admin
from .models import product, productMedia, category, brand, size, brand_category


class ProductMediaInline(admin.TabularInline):
    model = productMedia.ProductMedia
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "name",
        "price",
        "category",
        "brand",
        "size",
        "is_archived",
        "created_at",
    )
    list_filter = ("owner", "category", "brand", "size", "is_archived")
    search_fields = ("id", "name", "owner")
    ordering = ("created_at",)
    inlines = [ProductMediaInline]

    fieldsets = (
        ("Basic details", {"fields": ("name", "desp", "owner")}),
        ("Stats", {"fields": ("price", "stock")}),
        ("Sub-Fields", {"fields": ("category", "size", "brand")}),
        ("Status", {"fields": ("is_archived",)}),
    )

    add_fieldsets = (
        (
            "Create Product",
            {
                "fields": (
                    "name",
                    "desp",
                    "price",
                    "stock",
                    "owner",
                    "category",
                    "size",
                    "brand",
                    "is_archived",
                ),
            },
        ),
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "created_at",
    )
    search_fields = (
        "id",
        "name",
        "slug",
    )
    ordering = ("created_at",)
    fieldsets = (
        (
            "Category Details",
            {
                "fields": ("name", "slug", "parent"),
            },
        ),
    )
    add_fieldsets = (
        (
            "Create Category",
            {
                "fields": (
                    "name",
                    "slug",
                    "parent",
                ),
            },
        ),
    )


class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "logo",
        "website",
        "created_at",
    )
    search_fields = ("id", "name", "website")
    ordering = ("created_at",)
    fieldsets = (
        (
            "Brand Details",
            {
                "fields": ("name", "logo", "website"),
            },
        ),
    )


class SizeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "brand",
        "category",
        "created_at",
    )
    search_fields = (
        "id",
        "name",
        "brand",
        "category",
    )
    ordering = ("created_at", "name")
    fieldsets = (
        (
            "Size Details",
            {
                "fields": ("name", "brand", "category"),
            },
        ),
    )


class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "type", "url", "created_at")
    search_fields = ("id", "type", "product")


class BrandCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "category")
    search_fields = ("brand", "category")


admin.site.register(product.Product, ProductAdmin)
admin.site.register(productMedia.ProductMedia, ProductMediaAdmin)
admin.site.register(category.Category, CategoryAdmin)
admin.site.register(brand.Brand, BrandAdmin)
admin.site.register(size.Size, SizeAdmin)
admin.site.register(brand_category.BrandCategory, BrandCategoryAdmin)
