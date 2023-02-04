from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from users.models import Profile
from users.serializers import ProfileSerializer, AvatarSerializer

import base64

from utils.b64 import base64_to_file


class UserList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @swagger_auto_schema(tags=["Users"], operation_summary="Get all users")
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Users"], operation_summary="Create a new user")
    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            user = request.data.get("user", {})
            username = user.get("username", "")
            if User.objects.filter(username=username).exists():
                return Response({"detail": "User already exists"}, status=status.HTTP_409_CONFLICT)
            return self.create(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN
        )


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch", "delete"]

    @swagger_auto_schema(tags=["Users"], operation_summary="Get a user")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Users"], operation_summary="Update a user")
    def patch(self, request, *args, **kwargs):
        user = User.objects.filter(pk=kwargs.get("pk")).first()
        if user is None:
            return Response({"detail": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_staff or request.user == user:
            avatar = request.data.get("avatar", "")
            if avatar:
                request.data["avatar"] = base64_to_file(avatar)
            return self.partial_update(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN
        )

    @swagger_auto_schema(tags=["Users"], operation_summary="Delete a user")
    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            user = User.objects.filter(pk=kwargs.get("pk")).first()
            if user is None:
                return Response({"detail": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            if user == request.user:
                return Response({"detail": "You cannot delete yourself"}, status=status.HTTP_400_BAD_REQUEST)
            user.profile.avatar.delete()
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN
        )


class UploadAvatarView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = AvatarSerializer
    http_method_names = ["patch"]

    @swagger_auto_schema(tags=["Users"], operation_summary="Upload an avatar")
    def patch(self, request, *args, **kwargs):
        user = User.objects.filter(pk=kwargs.get("pk")).first()
        if user is None:
            return Response({"detail": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_staff or request.user == user:
            return self.partial_update(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN
        )
