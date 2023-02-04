import base64

from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import Profile
from utils.b64 import file_to_base64


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # Uncomment this field to get the avatar as base64 if frontend needs it
    # avatar_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = "__all__"

    # Uncomment this method to get the avatar as base64 if frontend needs it
    # def get_avatar_base64(self, profile):
    #     return file_to_base64(profile.avatar) if profile.avatar else ""

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        random_password = User.objects.make_random_password()
        user_data["password"] = random_password
        user = User.objects.create(**user_data)

        profile = Profile.objects.get(user=user)
        profile.__dict__.update(validated_data)
        profile.save()

        return profile


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar"]
