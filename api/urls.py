from django.urls import path, include

urlpatterns = [
    path("", include("users.urls")),
    path("", include("product.urls")),
    path("", include("cart.urls")),
    path("", include("address.urls")),
    path("", include("coupons.urls")),
    path("", include("orders.urls")),
    path("", include("delivery.urls")),
    path("", include("disputes.urls")),
    path("", include("transaction.urls")),
    path("", include("review.urls")),
]
