from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserAllProfileView, UserChangeRoleView, UserEditProfileView, UserOtherProfileView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user/register/', UserRegistrationView.as_view(), name='register'),
    path('user/login/', UserLoginView.as_view(), name='login'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='refresh access token'),
    path('user/logout/', UserLogoutView.as_view(), name='logout'),
    path('user/profile/', UserProfileView.as_view(), name='profile'),
    path('user/other/<uuid:pk>/', UserOtherProfileView.as_view(), name='other user profile'),
    path('user/all/', UserAllProfileView.as_view(), name='all user profile(admin only)'),
    path('user/edit/profile/', UserEditProfileView.as_view(), name='edit profile'),
    path('user/role/<uuid:pk>/', UserChangeRoleView.as_view(), name='change role(admin only)'),
]
