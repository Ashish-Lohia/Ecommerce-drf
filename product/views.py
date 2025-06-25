from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from .serializer import (
    CreateBrandSerializer,
    CreateCategorySerializer,
    CreateProductMediaSerializer,
    CreateProductSerializer,
    CreateSizeSerializer,
)
from .models import Product, ProductMedia, Category, Brand, Size
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class BrandView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        brands = Brand.objects.all()
        serializer = CreateBrandSerializer(brands, many=True)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = CreateBrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Brand created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatedeleteBrandView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        serializer = CreateBrandSerializer(brand, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Brand updated successfully"},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        brand.delete()
        return Response(
            {"success": True, "message": "Brand deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
