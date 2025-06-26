from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from product.models import Brand, Category, BrandCategory
from product.serializers import (
    BrandCategorySerializer,
    BrandCategoryDetailSerializer,
)
from rest_framework.permissions import IsAdminUser


class BrandCategoryViewSet(viewsets.ModelViewSet):
    queryset = BrandCategory.objects.all().select_related("brand", "category")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["brand", "category"]
    search_fields = ["brand__name", "category__name", "category__slug"]
    ordering_fields = ["brand__name", "category__name", "created_at", "updated_at"]
    ordering = ["brand__name", "category__name"]
    permission_classes = [IsAdminUser]

    def format_response(self, data, success=True, message=None, status_code=None):
        response_data = {"success": success, "data": data}
        if message:
            response_data["message"] = message

        return Response(response_data, status=status_code)

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return BrandCategoryDetailSerializer
        return BrandCategorySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.format_response(response.data, status_code=response.status_code)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.format_response(
            response.data,
            message="Brand created successfully",
            status_code=response.status_code,
        )

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self.format_response(response.data, status_code=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.format_response(
            response.data,
            message="Brand updated successfully",
            status_code=response.status_code,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return self.format_response(
            None, message="Brand deleted successfully", status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):
        relationships = request.data.get("relationships", [])

        if not relationships:
            return Response(
                {"error": "relationships list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_relationships = []
        errors = []

        for rel in relationships:
            serializer = BrandCategorySerializer(data=rel)
            if serializer.is_valid():
                try:
                    brand_category = serializer.save()
                    created_relationships.append(
                        BrandCategoryDetailSerializer(
                            brand_category, context={"request": request}
                        ).data
                    )
                except Exception as e:
                    errors.append({"relationship": rel, "error": str(e)})
            else:
                errors.append({"relationship": rel, "errors": serializer.errors})

        return Response(
            {
                "success": True,
                "created": created_relationships,
                "errors": errors,
                "created_count": len(created_relationships),
                "error_count": len(errors),
            },
            status=(
                status.HTTP_201_CREATED
                if created_relationships
                else status.HTTP_400_BAD_REQUEST
            ),
        )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        total_relationships = self.queryset.count()
        total_brands = Brand.objects.count()
        total_categories = Category.objects.count()

        brands_with_categories = (
            Brand.objects.annotate(category_count=Count("brand_categories"))
            .filter(category_count__gt=0)
            .count()
        )

        categories_with_brands = (
            Category.objects.annotate(brand_count=Count("category_brands"))
            .filter(brand_count__gt=0)
            .count()
        )

        return self.format_response(
            {
                "success": True,
                "total_relationships": total_relationships,
                "total_brands": total_brands,
                "total_categories": total_categories,
                "brands_with_categories": brands_with_categories,
                "categories_with_brands": categories_with_brands,
                "brands_without_categories": total_brands - brands_with_categories,
                "categories_without_brands": total_categories - categories_with_brands,
            },
            message="Brand-Category pairs stats fetched successfully",
            status_code=status.HTTP_201_CREATED,
        )
