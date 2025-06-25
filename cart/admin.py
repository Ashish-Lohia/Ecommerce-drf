from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "get_total_items", "get_total_price")
    list_filter = ("owner",)
    search_fields = ("id", "owner__id")
    inlines = [CartItemInline]
    fieldsets = (("Cart Details", {"fields": ("owner",)}),)

    def get_total_items(self, obj):
        return obj.get_total_items()

    get_total_items.short_description = "Total Items"

    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = "Total Price"


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity")
    list_filter = ("cart", "product")
    search_fields = ("id", "cart__id", "product__name")
    fieldsets = (("Cart Item Details", {"fields": ("cart", "product", "quantity")}),)


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
