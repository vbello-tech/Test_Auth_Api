from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile
from .serializers import RegisterSerializer, ProfileSerializer, LoginSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenObtainPairSerializer, \
    TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

class RegisterView(GenericAPIView):
    """
    Signup view
    """
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = serializer.data
        return Response({
            "message": "Registered successfully.",
            "data": data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    Login view
    """
    serializer_class = TokenObtainPairSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, email=email, password=password)
        tokens = super().post(request)
        if user:
            return Response({
                "message": "Login successful",
                "data": {
                    "full_name": user.username,
                    "email": user.email,
                    "refresh": tokens.data["refresh"],
                    'access': tokens.data["access"],
                }
            }, status=status.HTTP_200_OK)
        elif not User.objects.filter(email).exists():
            return Response({"message": "User accounts does not exist"},
                            status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message": "Email or Password incorrect"},
                            status=status.HTTP_400_BAD_REQUEST)


class ProfileView(GenericAPIView):
    """
    Update Profile View
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = Profile.objects.filter(user=request.user)
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.bio = serializer.validated_data["bio"]
        user.twitter = serializer.validated_data["twitter"]
        user.github = serializer.validated_data["github"]
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_user(request):
    """
    Get logged in user profile
    """
    try:
        user_p = get_object_or_404(Profile, user=request.user)
        return Response({
            'message': "Profile fetched successfully",
            "data": {
                "bio": user_p.bio,
                "twitter": user_p.twitter,
                "github": user_p.github
            }
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({
            'message': "You dont have a profile",
        })


class LogoutView(TokenBlacklistView):
    """
    Logout users with refresh token
    """
    serializer_class = TokenBlacklistSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"message": "Token is blacklisted."},
                            status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]
        if old_password == new_password:
            return Response({
                "message": "New password most be different from Old password.",
                "password": new_password
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "Password changed successfully.",
                "password": new_password
            }, status=status.HTTP_200_OK)
