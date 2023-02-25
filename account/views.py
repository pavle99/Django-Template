from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import (
    AccountSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    SetPasswordSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from utils.mail import send_set_password_email


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(tags=["Auth"], operation_summary="Login a user")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    serializer_class = RefreshTokenSerializer

    @swagger_auto_schema(tags=["Auth"], operation_summary="Refresh access token")
    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.data.pop("refresh_token")
        return super().post(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @swagger_auto_schema(tags=["Auth"], operation_summary="Register a new user")
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        if User.objects.filter(username=username).exists():
            return Response({"detail": "User already exists"}, status=status.HTTP_409_CONFLICT)

        user = User.objects.create_user(
            username=username, email=email, password=password, first_name=first_name, last_name=last_name, is_staff=True
        )
        user.save()

        return Response({"detail": "User created successfully"}, status=status.HTTP_201_CREATED)


class GetCurrentUserView(generics.RetrieveAPIView):
    serializer_class = AccountSerializer

    @swagger_auto_schema(tags=["Auth"], operation_summary="Get current user")
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(tags=["Auth"], operation_summary="Change password")
    def patch(self, request, *args, **kwargs):
        old_password = request.data.get("old_password", "")
        new_password = request.data.get("new_password", "")
        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer

    @swagger_auto_schema(tags=["Auth"], operation_summary="Send set password email")
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        user = User.objects.filter(email=email).first()
        if user is not None and user.is_active:
            send_set_password_email(user)
            return Response({"detail": "Email sent successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "User not found"}, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    permission_classes = [permissions.AllowAny]
    serializer_class = SetPasswordSerializer

    @swagger_auto_schema(tags=["Auth"], operation_summary="Set password")
    def patch(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        token = request.data.get("token", "")
        new_password = request.data.get("new_password", "")
        user = User.objects.filter(email=email).first()
        if user is not None and user.is_active and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password set successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
