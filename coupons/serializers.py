from rest_framework import serializers
from coupons.models import Coupon, CouponUser
from users.serializers import UserProfileSerializer


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "type",
            "value",
            "max_value",
            "min_order_value",
            "valid_from",
            "valid_to",
            "is_active",
            "max_use",
            "used_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["used_count", "created_at", "updated_at"]


class CouponUserSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    coupon = serializers.StringRelatedField()

    class Meta:
        model = CouponUser
        fields = ["id", "coupon", "user", "used_at"]
