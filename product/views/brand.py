from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from product.models import Brand, Category, BrandCategory
from product.serializers import (
    BrandSerializer,
    BrandListSerializer,
    CategoryListSerializer,
    BrandCategorySerializer,
    SizeListSerializer,
)
from product.filters import BrandFilter
from rest_framework.permissions import IsAdminUser


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().prefetch_related("brand_categories__category")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]
    filterset_class = BrandFilter

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Admin-only actions: create, update, partial_update, destroy, add_category, remove_category
        Public actions: list, retrieve, categories, sizes
        """
        admin_only_actions = [
            "create",
            "update",
            "partial_update",
            "destroy",
            "add_category",
            "remove_category",
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
            return BrandListSerializer
        return BrandSerializer

    def list(self, request, *args, **kwargs):
        """Override list method to format response"""
        response = super().list(request, *args, **kwargs)
        return self.format_response(response.data, status_code=response.status_code)

    def create(self, request, *args, **kwargs):
        """Override create method to format response"""
        response = super().create(request, *args, **kwargs)
        return self.format_response(
            response.data,
            message="Brand created successfully",
            status_code=response.status_code,
        )

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve method to format response"""
        response = super().retrieve(request, *args, **kwargs)
        return self.format_response(response.data, status_code=response.status_code)

    def update(self, request, *args, **kwargs):
        """Override update method to format response"""
        response = super().update(request, *args, **kwargs)
        return self.format_response(
            response.data,
            message="Brand updated successfully",
            status_code=response.status_code,
        )

    def destroy(self, request, *args, **kwargs):
        """Override destroy method to format response"""
        super().destroy(request, *args, **kwargs)
        return self.format_response(
            None, message="Brand deleted successfully", status_code=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"])
    def categories(self, request, pk=None):
        """Get all categories associated with this brand"""
        brand = self.get_object()
        brand_categories = brand.brand_categories.all().select_related("category")
        categories = [bc.category for bc in brand_categories]
        serializer = CategoryListSerializer(
            categories, many=True, context={"request": request}
        )
        return self.format_response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_category(self, request, pk=None):
        """Add a category to this brand"""
        brand = self.get_object()
        category_id = request.data.get("category_id")

        if not category_id:
            return self.format_response(
                None,
                success=False,
                message="category_id is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return self.format_response(
                None,
                success=False,
                message="Category not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        brand_category, created = BrandCategory.objects.get_or_create(
            brand=brand, category=category
        )

        if created:
            serializer = BrandCategorySerializer(
                brand_category, context={"request": request}
            )
            return self.format_response(
                serializer.data,
                message="Category added to brand successfully",
                status_code=status.HTTP_201_CREATED,
            )
        else:
            return self.format_response(
                None,
                message="Brand-Category relationship already exists",
                status_code=status.HTTP_200_OK,
            )

    @action(detail=True, methods=["delete"])
    def remove_category(self, request, pk=None):
        """Remove a category from this brand"""
        brand = self.get_object()
        category_id = request.data.get("category_id")

        if not category_id:
            return self.format_response(
                None,
                success=False,
                message="category_id is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            brand_category = BrandCategory.objects.get(
                brand=brand, category_id=category_id
            )
            brand_category.delete()
            return self.format_response(
                None,
                message="Category removed from brand successfully",
                status_code=status.HTTP_200_OK,
            )
        except BrandCategory.DoesNotExist:
            return self.format_response(
                None,
                success=False,
                message="Brand-Category relationship not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"])
    def sizes(self, request, pk=None):
        """Get all sizes for this brand"""
        brand = self.get_object()
        sizes = brand.sizes.all().select_related("category")
        serializer = SizeListSerializer(sizes, many=True, context={"request": request})
        return self.format_response(serializer.data)
