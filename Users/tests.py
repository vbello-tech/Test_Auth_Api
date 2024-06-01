import random, json
from datetime import timedelta
from requests.auth import HTTPBasicAuth
from .models import User
from .serializers import RegisterSerializer
from django.contrib.auth.hashers import check_password
from django.urls import reverse_lazy, reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# Create your tests here.

client = APIClient()


class RegisterTest(APITestCase):

    def setUp(self):
        self.data = {
            "email": "temi@gmail.com",
            "password": "temi15n347",
            "username": "temi",
        }

    def test_register(self):
        response = client.post(reverse_lazy("register"), self.data, format="json")
        serializer = RegisterSerializer(self.data)
        self.assertEqual(response.data['data'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginProfileTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bello", password="flash2014", email="me@gmail.com",
        )
        self.data = {
            "email": self.user.email,
            "password": self.user.password,
        }

    def test_login(self):
        login_data = {
            "email": self.data["email"],
            "password": self.data["password"]
        }
        if check_password(login_data["password"], self.user.password):
            refresh = RefreshToken.for_user(self.user)
            response = client.post(reverse_lazy("login"), login_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return self.User.objects.get()

    def test_unregistered_email(self):
        login_data = {
            "email": "unknown@gmail.com",
            "password": self.data["password"]
        }
        response = client.post(reverse_lazy("login"), login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_password(self):
        login_data = {
            "email": self.data["email"],
            "password": "wrong_password"
        }
        response = client.post(reverse_lazy("login"), login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_unauthenticated(self):
        response = client.get(reverse_lazy("get_profile"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_authenticated(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user, token=str(refresh.access_token))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        response = self.client.get(reverse_lazy("get_profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)
        client.force_authenticate(user=self.user, token=str(refresh.access_token))
        logout_data = {"refresh": str(refresh)}
        response = client.post(reverse_lazy("logout"), logout_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        refresh = RefreshToken.for_user(self.user)
        client.force_authenticate(user=self.user, token=str(refresh.access_token))
        password_data = {"old_password": "old_password", "new_password": "new_password"}
        response = client.post(reverse_lazy("change_password"), password_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_same_old(self):
        refresh = RefreshToken.for_user(self.user)
        client.force_authenticate(user=self.user, token=str(refresh.access_token))
        password_data = {"old_password": "old_password", "new_password": "old_password"}
        response = client.post(reverse_lazy("change_password"), password_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
