from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from product.models import Product
from product.serializers import (
    ProductSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)
from product.filters import ProductFilter
from rest_framework.response import Response
from rest_framework import permissions


class IsSellerOrAdminAndOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            return True

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if view.action == "create":
            return user.role == "seller" or user.is_staff

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin can do anything
        if user.is_staff:
            return True

        return user.role == "seller" and obj.owner == user


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related(
        "brand", "category", "size", "owner"
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name", "brand__name", "category__name", "owner__fullname"]
    ordering_fields = ["price", "stock", "created_at"]
    ordering = ["-created_at"]
    permission_classes = [IsSellerOrAdminAndOwner]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        elif self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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
                "message": "Product created successfully",
                "data": response.data,
            },
            status=response.status_code,
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "Product updated successfully",
                "data": response.data,
            },
            status=response.status_code,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"success": True, "message": "Product deleted successfully"},
            status=status.HTTP_200_OK,
        )
