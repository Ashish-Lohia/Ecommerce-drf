from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from product.models import Category, BrandCategory
from product.serializers import (
    BrandListSerializer,
    CategorySerializer,
    CategoryListSerializer,
    SizeListSerializer,
)
from product.filters import CategoryFilter
from rest_framework.permissions import IsAdminUser


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related("children", "parent")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["parent"]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]
    filterset_class = CategoryFilter

    def get_permissions(self):
        """Define which actions require admin permissions"""
        admin_only_actions = [
            "create",
            "update",
            "partial_update",
            "destroy",
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
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return CategoryListSerializer
        return CategorySerializer

    def list(self, request, *args, **kwargs):
        """List all categories with formatted response"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)
                return self.format_response(
                    data=paginated_response.data,
                    message="Categories retrieved successfully",
                    status_code=status.HTTP_200_OK,
                )

            serializer = self.get_serializer(queryset, many=True)
            return self.format_response(
                data=serializer.data,
                message="Categories retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error retrieving categories: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single category with formatted response"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.format_response(
                data=serializer.data,
                message="Category retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error retrieving category: {str(e)}",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """Create a new category with formatted response"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return self.format_response(
                    data=serializer.data,
                    message="Category created successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                return self.format_response(
                    data=serializer.errors,
                    success=False,
                    message="Validation error",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error creating category: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """Update a category with formatted response"""
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )

            if serializer.is_valid():
                self.perform_update(serializer)
                return self.format_response(
                    data=serializer.data,
                    message="Category updated successfully",
                    status_code=status.HTTP_200_OK,
                )
            else:
                return self.format_response(
                    data=serializer.errors,
                    success=False,
                    message="Validation error",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error updating category: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def partial_update(self, request, *args, **kwargs):
        """Partially update a category with formatted response"""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete a category with formatted response"""
        try:
            instance = self.get_object()
            category_name = instance.name
            self.perform_destroy(instance)
            return self.format_response(
                data=None,
                message=f"Category '{category_name}' deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error deleting category: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def root_categories(self, request):
        """Get all root categories (categories with no parent)"""
        try:
            root_categories = self.queryset.filter(parent__isnull=True)
            serializer = self.get_serializer(root_categories, many=True)
            return self.format_response(
                data=serializer.data,
                message="Root categories retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error retrieving root categories: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        """Get all direct children of a category"""
        try:
            category = self.get_object()
            children = category.children.all()
            serializer = self.get_serializer(children, many=True)
            return self.format_response(
                data=serializer.data,
                message=f"Children of category '{category.name}' retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error retrieving category children: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def brands(self, request, pk=None):
        """Get all brands associated with this category"""
        try:
            category = self.get_object()
            brand_categories = BrandCategory.objects.filter(
                category=category
            ).select_related("brand")
            brands = [bc.brand for bc in brand_categories]
            serializer = BrandListSerializer(
                brands, many=True, context={"request": request}
            )
            return self.format_response(
                data=serializer.data,
                message=f"Brands for category '{category.name}' retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error retrieving category brands: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def sizes(self, request, pk=None):
        """Get all sizes for this category"""
        try:
            category = self.get_object()
            sizes = category.sizes.all().select_related("brand")
            serializer = SizeListSerializer(
                sizes, many=True, context={"request": request}
            )
            return self.format_response(
                data=serializer.data,
                message=f"Sizes for category '{category.name}' retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error retrieving category sizes: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """Get the complete category tree structure"""
        try:
            root_categories = self.queryset.filter(parent__isnull=True)
            serializer = CategorySerializer(
                root_categories, many=True, context={"request": request}
            )
            return self.format_response(
                data=serializer.data,
                message="Category tree retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.format_response(
                data=None,
                success=False,
                message=f"Error retrieving category tree: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
