from rest_framework import generics, status
from rest_framework.views import APIView
from .models import User
from .serializers import (
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    OtherUserProfileSerializer,
    AllUserProfileSerializer,
    EditUserProfileSerializer,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
import logging
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        logger.info(f"User logged in: {user.email}")

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "User loggedIn successfully",
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "fullname": user.fullname,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        try:
            refresh_token = request.data["refresh_token"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"success": True, "message": "User Logout successfully"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except KeyError:
            return Response(
                {"error": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST
            )
        except TokenError:
            return Response(
                {"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserOtherProfileView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = OtherUserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAllProfileView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AllUserProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserEditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serialier = EditUserProfileSerializer(
            request.user, data=request.data, context={"request": request}
        )
        if serialier.is_valid():
            serialier.save()
            return Response(
                {"success": True, "message": "Profile Updated Successfully"},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(serialier.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChangeRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        role = request.data.get("role")
        valid_roles = [choice[0] for choice in User.role_choices]
        if not role:
            return Response(
                {"success": False, "message": "Role is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if role not in valid_roles:
            return Response(
                {
                    "success": False,
                    "message": "Role should be buyer, seller or admin only.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.role = role
        if role == "superadmin":
            user.is_staff = True
            user.is_superuser = True
        elif role == "admin":
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = False
        user.save()
        return Response(
            {"success": True, "message": "User role updated successfully."},
            status=status.HTTP_200_OK,
        )
