from rest_framework import generics, status
from users.models import User
from users.serializers import UserLoginSerializer, UserRegistrationSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        logger.info(f"User logged in: {user.email}")

        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': "User loggedIn successfully",
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'fullname': user.fullname,
                'role': user.role
            }
        }, status=status.HTTP_200_OK)
