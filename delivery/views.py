from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from delivery.models import Delivery
from delivery.serializers import DeliverySerializer, DeliveryListSerializer


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all().select_related("order")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "provider", "order", "created_at"]
    ordering_fields = ["created_at", "estimated_delivery_date"]
    ordering = ["-created_at"]
    search_fields = ["tracking_id", "order__id"]

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "change_status",
        ]:
            return [IsAdminOnly()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return DeliveryListSerializer
        return DeliverySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "Delivery created successfully",
                "data": response.data,
            },
            status=response.status_code,
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "Delivery updated successfully",
                "data": response.data,
            },
            status=response.status_code,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"success": True, "message": "Delivery deleted successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="change-status")
    def change_status(self, request, pk=None):
        delivery = self.get_object()
        status_value = request.data.get("status")

        if status_value not in dict(Delivery.STATUS_CHOICES).keys():
            return Response(
                {"success": False, "message": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery.status = status_value
        delivery.save()

        return Response(
            {
                "success": True,
                "message": f"Status updated to {status_value}",
                "data": DeliverySerializer(delivery).data,
            }
        )
