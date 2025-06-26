from django.urls import path, include
from rest_framework.routers import DefaultRouter
from coupons.views import CouponViewSet, CouponUserViewSet

router = DefaultRouter()
router.register("coupons", CouponViewSet, basename="coupon")
router.register("my-coupons", CouponUserViewSet, basename="couponuser")

urlpatterns = [
    path("", include(router.urls)),
]
