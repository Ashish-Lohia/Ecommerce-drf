from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from orders.models import Order
from orders.serializers import OrderSerializer
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBuyerOrSellerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user == obj.buyer
                or request.user == obj.seller
                or request.user.is_superuser
            )
        )


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuyerOrSellerOrAdmin]

    queryset = (
        Order.objects.all()
        .select_related("buyer", "seller", "coupons")
        .prefetch_related("order_items__product")
    )

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["status", "buyer", "seller", "created_at"]
    ordering_fields = ["created_at", "total_amount", "status"]
    ordering = ["-created_at"]
    search_fields = ["buyer__fullname", "seller__fullname", "id"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(Q(buyer=user) | Q(seller=user))

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

    def retrieve(self, request, *args, **kwargs):
        self.queryset = (
            self.get_queryset()
            .select_related("user", "coupon")
            .prefetch_related(
                "order_items", "order_items__product", "order_items__product__brand"
            )
        )
        response = super().retrieve(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "Order updated successfully",
                "data": response.data,
            }
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True, "message": "Order deleted successfully"})

    @action(
        detail=True,
        methods=["patch"],
        url_path="change-status",
        permission_classes=[permissions.IsAdminUser],
    )
    def change_status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get("status")
        valid_statuses = dict(Order.STATUS_CHOICES).keys()

        if status_value not in valid_statuses:
            return Response(
                {"success": False, "message": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = status_value
        if status_value == "completed":
            from django.utils import timezone

            order.completed_at = timezone.now()
        order.save()

        return Response(
            {
                "success": True,
                "message": f"Order status changed to '{status_value}'",
                "data": OrderSerializer(order, context={"request": request}).data,
            }
        )
