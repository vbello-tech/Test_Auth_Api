from django.urls import path, include
from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    get_user,
    LogoutView,
    ChangePasswordView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('token/', TokenObtainPairView.as_view(), name="obtain_token"),  # login url
    path('user/me/', get_user, name="get_profile"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('change-password/', ChangePasswordView.as_view(), name="change_password"),
]
