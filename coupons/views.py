from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from coupons.models import Coupon, CouponUser
from coupons.serializers import CouponSerializer, CouponUserSerializer


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def active(self, request):
        """List active and valid coupons for user"""
        current_time = now()
        valid_coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=current_time,
            valid_to__gte=current_time,
        ).exclude(users__user=request.user)

        serializer = self.get_serializer(valid_coupons, many=True)
        return Response({"success": True, "data": serializer.data})


class CouponUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CouponUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CouponUser.objects.filter(user=self.request.user).select_related(
            "coupon", "user"
        )

    @action(detail=False, methods=["post"])
    def use_coupon(self, request):
        """Mark coupon as used by user"""
        code = request.data.get("code")
        if not code:
            return Response(
                {"error": "Coupon code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response(
                {"error": "Invalid or inactive coupon code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if coupon.valid_from > now() or coupon.valid_to < now():
            return Response(
                {"error": "Coupon is not valid at this time"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if CouponUser.objects.filter(coupon=coupon, user=request.user).exists():
            return Response(
                {"error": "You have already used this coupon"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if coupon.used_count >= coupon.max_use:
            return Response(
                {"error": "Coupon usage limit reached"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        CouponUser.objects.create(user=request.user, coupon=coupon)
        coupon.update_used_count()

        return Response(
            {"success": True, "message": "Coupon applied successfully"},
            status=status.HTTP_200_OK,
        )
