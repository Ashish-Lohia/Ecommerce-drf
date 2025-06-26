from django.urls import path, include
from rest_framework.routers import DefaultRouter
from disputes.views import DisputeViewSet, DisputeMediaViewSet

router = DefaultRouter()
router.register(r"disputes", DisputeViewSet, basename="dispute")
router.register(r"dispute-media", DisputeMediaViewSet, basename="dispute-media")

urlpatterns = [
    path("", include(router.urls)),
]
