from django.contrib.auth.models import User
from rest_framework import serializers

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from users.models import Profile


class LoginSerializer(TokenObtainPairSerializer):
    default_error_messages = {"no_active_account": "Invalid credentials!"}

    def validate(self, attrs):
        data = super().validate(attrs)

        #         rename refresh to refresh_token
        data["refresh_token"] = data.pop("refresh")
        data["access_token"] = data.pop("access")

        return data


class RefreshTokenSerializer(TokenRefreshSerializer):
    class Meta:
        fields = ("refresh_token",)

    def validate(self, attrs):
        data = super().validate(attrs)

        data["access_token"] = data.pop("access")

        return data


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        profile = Profile.objects.get(user=instance)
        ret["avatar"] = profile.avatar.url if profile.avatar else ""
        return ret


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
