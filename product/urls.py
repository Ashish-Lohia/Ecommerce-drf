from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BrandCategoryViewSet,
    BrandViewSet,
    CategoryViewSet,
    SizeViewSet,
    ProductViewSet,
)

router = DefaultRouter()
router.register(r"brands", BrandViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"brand-categories", BrandCategoryViewSet)
router.register(r"sizes", SizeViewSet)
router.register(r"products", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
