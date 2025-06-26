from rest_framework import serializers
from disputes.models import Dispute, DisputeMedia


class DisputeMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeMedia
        fields = ["id", "dispute", "type", "url", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DisputeSerializer(serializers.ModelSerializer):
    multimedia = DisputeMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Dispute
        fields = [
            "id",
            "user",
            "order",
            "content",
            "status",
            "result",
            "multimedia",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "result",
            "created_at",
            "updated_at",
            "user",
        ]
