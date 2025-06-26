from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from disputes.models import Dispute, DisputeMedia
from disputes.serializers import DisputeSerializer, DisputeMediaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user


class DisputeViewSet(viewsets.ModelViewSet):
    queryset = (
        Dispute.objects.all()
        .select_related("user", "order")
        .prefetch_related("multimedia")
    )
    serializer_class = DisputeSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["status", "user", "order", "created_at"]
    search_fields = ["content", "result"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "Dispute created successfully",
                "data": response.data,
            },
            status=response.status_code,
        )

    @action(detail=True, methods=["patch"], permission_classes=[IsOwnerOrAdmin])
    def resolve(self, request, pk=None):
        dispute = self.get_object()
        if dispute.status not in ["created", "pending"]:
            return Response(
                {"success": False, "message": "Dispute cannot be resolved."}, status=400
            )
        dispute.status = "resolved"
        dispute.result = request.data.get("result", dispute.result)
        dispute.save()
        return Response(
            {
                "success": True,
                "message": "Dispute resolved.",
                "data": DisputeSerializer(dispute).data,
            }
        )


class DisputeMediaViewSet(viewsets.ModelViewSet):
    queryset = DisputeMedia.objects.all().select_related("dispute")
    serializer_class = DisputeMediaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["dispute", "type"]
    ordering = ["-created_at"]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"success": True, "data": response.data})

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"success": True, "message": "Media uploaded", "data": response.data}
        )
