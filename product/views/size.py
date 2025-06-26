from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from product.models import Brand, Category, BrandCategory, Size
from product.serializers import (
    SizeSerializer,
    SizeDetailSerializer,
    SizeListSerializer,
)
from product.filters import SizeFilter
from rest_framework.permissions import IsAdminUser


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all().select_related("brand", "category")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["brand", "category", "name"]
    search_fields = ["name", "brand__name", "category__name", "category__slug"]
    ordering_fields = [
        "name",
        "brand__name",
        "category__name",
        "created_at",
        "updated_at",
    ]
    ordering = ["brand__name", "category__name", "name"]
    filterset_class = SizeFilter

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Admin-only actions: create, update, partial_update, destroy, bulk_create
        Public actions: list, retrieve, by_brand_category, stats, duplicate_names
        """
        admin_only_actions = [
            "create",
            "update",
            "partial_update",
            "destroy",
            "bulk_create",
        ]

        if self.action in admin_only_actions:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    def format_response(self, data, success=True, message=None, status_code=None):
        """Helper method to format all responses consistently"""
        response_data = {"success": success, "data": data}
        if message:
            response_data["message"] = message

        return Response(response_data, status=status_code)

    def get_serializer_class(self):
        if self.action == "list":
            return SizeListSerializer
        elif self.action == "retrieve":
            return SizeDetailSerializer
        return SizeSerializer

    def list(self, request, *args, **kwargs):
        """List all sizes with pagination and filtering"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return self.format_response(
                data=paginated_response.data,
                message="Sizes retrieved successfully",
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(queryset, many=True)
        return self.format_response(
            data=serializer.data,
            message="Sizes retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific size"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.format_response(
            data=serializer.data,
            message="Size retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """Create a new size (Admin only)"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            size = serializer.save()
            return self.format_response(
                data=SizeDetailSerializer(size, context={"request": request}).data,
                message="Size created successfully",
                status_code=status.HTTP_201_CREATED,
            )
        else:
            return self.format_response(
                data=serializer.errors,
                success=False,
                message="Validation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        """Update a size (Admin only)"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            size = serializer.save()
            return self.format_response(
                data=SizeDetailSerializer(size, context={"request": request}).data,
                message="Size updated successfully",
                status_code=status.HTTP_200_OK,
            )
        else:
            return self.format_response(
                data=serializer.errors,
                success=False,
                message="Validation failed",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, *args, **kwargs):
        """Partially update a size (Admin only)"""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete a size (Admin only)"""
        instance = self.get_object()
        size_name = instance.name
        instance.delete()
        return self.format_response(
            data=None,
            message=f"Size '{size_name}' deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=["get"])
    def by_brand_category(self, request):
        """Get sizes filtered by brand and category"""
        brand_id = request.query_params.get("brand_id")
        category_id = request.query_params.get("category_id")

        if not brand_id or not category_id:
            return self.format_response(
                data=None,
                success=False,
                message="Both brand_id and category_id are required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that the brand-category combination exists
        if not BrandCategory.objects.filter(
            brand_id=brand_id, category_id=category_id
        ).exists():
            return self.format_response(
                data=None,
                success=False,
                message="Brand-Category combination does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        sizes = self.queryset.filter(brand_id=brand_id, category_id=category_id)
        serializer = self.get_serializer(sizes, many=True)
        return self.format_response(
            data=serializer.data,
            message="Sizes retrieved successfully for brand-category combination",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):
        """Create multiple sizes at once (Admin only)"""
        sizes_data = request.data.get("sizes", [])

        if not sizes_data:
            return self.format_response(
                data=None,
                success=False,
                message="sizes list is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        created_sizes = []
        errors = []

        for size_data in sizes_data:
            serializer = SizeSerializer(data=size_data)
            if serializer.is_valid():
                try:
                    size = serializer.save()
                    created_sizes.append(
                        SizeDetailSerializer(size, context={"request": request}).data
                    )
                except Exception as e:
                    errors.append({"size_data": size_data, "error": str(e)})
            else:
                errors.append({"size_data": size_data, "errors": serializer.errors})

        response_data = {
            "created": created_sizes,
            "errors": errors,
            "created_count": len(created_sizes),
            "error_count": len(errors),
        }

        if created_sizes:
            return self.format_response(
                data=response_data,
                message=f"Bulk create completed: {len(created_sizes)} created, {len(errors)} failed",
                status_code=status.HTTP_201_CREATED,
            )
        else:
            return self.format_response(
                data=response_data,
                success=False,
                message="No sizes were created",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get statistics about sizes"""
        total_sizes = self.queryset.count()
        unique_size_names = self.queryset.values("name").distinct().count()
        brands_with_sizes = Brand.objects.filter(sizes__isnull=False).distinct().count()
        categories_with_sizes = (
            Category.objects.filter(sizes__isnull=False).distinct().count()
        )
        common_sizes = (
            self.queryset.values("name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        stats_data = {
            "total_sizes": total_sizes,
            "unique_size_names": unique_size_names,
            "brands_with_sizes": brands_with_sizes,
            "categories_with_sizes": categories_with_sizes,
            "most_common_sizes": common_sizes,
        }

        return self.format_response(
            data=stats_data,
            message="Size statistics retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def duplicate_names(self, request):
        # Step 1: Group by name and count total appearances
        duplicates = (
            self.queryset.values("name")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
            .order_by("-count")
        )

        # Optional: Add count of unique brand-category combinations in Python
        brand_cat_combinations = {}
        for item in self.queryset.values("name", "brand", "category"):
            key = item["name"]
            brand_cat_combinations.setdefault(key, set()).add(
                (item["brand"], item["category"])
            )

        for entry in duplicates:
            name = entry["name"]
            entry["brand_category_combinations"] = len(
                brand_cat_combinations.get(name, [])
            )

        # Response structure
        duplicate_data = {
            "duplicate_size_names": list(duplicates),
            "total_duplicates": len(duplicates),
        }

        return Response(data=duplicate_data, status=status.HTTP_200_OK)
