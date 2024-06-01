from rest_framework import serializers
from .models import User, Profile


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(max_length=200, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')

        return attrs


class ProfileSerializer(serializers.Serializer):
    user = serializers.CharField(read_only=True)
    bio = serializers.CharField()
    twitter = serializers.URLField()
    github = serializers.URLField()

    def create(self, validated_data):
        return Profile.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
