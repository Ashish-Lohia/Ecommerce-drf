from django.urls import path
from .views import BrandView, UpdatedeleteBrandView


urlpatterns = [
    path("brand/", BrandView.as_view(), name="Create and get Brands"),
    path(
        "brand/<uuid:pk>/",
        UpdatedeleteBrandView.as_view(),
        name="Update and Delete Brand",
    ),
]
