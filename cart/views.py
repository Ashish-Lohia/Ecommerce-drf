from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cart.models import Cart, CartItem
from cart.serializer import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(owner=self.request.user).prefetch_related(
            "cart_items__product"
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            cart = Cart.objects.create(owner=request.user)
        return self.retrieve(request, pk=queryset.first().pk)

    def retrieve(self, request, *args, **kwargs):
        cart = self.get_queryset().first()
        if not cart:
            cart = Cart.objects.create(owner=request.user)
        serializer = self.get_serializer(cart)
        return Response({"success": True, "data": serializer.data})


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__owner=self.request.user).select_related(
            "product"
        )

    def perform_create(self, serializer):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(owner=user)
        serializer.save(cart=cart)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        self.perform_destroy(item)
        return Response(
            {"success": True, "message": "Item removed from cart"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "Cart item updated successfully",
                "data": response.data,
            },
            status=response.status_code,
        )
