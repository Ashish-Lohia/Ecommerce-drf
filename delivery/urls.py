from rest_framework.routers import DefaultRouter
from delivery.views import DeliveryViewSet

router = DefaultRouter()
router.register(r"deliveries", DeliveryViewSet, basename="delivery")
urlpatterns = router.urls
