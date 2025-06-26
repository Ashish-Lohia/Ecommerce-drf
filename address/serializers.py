from rest_framework import serializers
from users.models import User
from address.models import Address


class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Address
        fields = [
            "id",
            "user",
            "address_line",
            "landmark",
            "city",
            "state",
            "country",
            "pin_code",
            "full_address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "full_address", "created_at", "updated_at"]

    def get_full_address(self, obj):
        return obj.get_full_address()
