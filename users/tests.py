import base64
from django.test import TestCase
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO

from users.models import Profile
from users.serializers import ProfileSerializer


class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user", password="test_password", email="test@test.com")

    def tearDown(self) -> None:
        profile = Profile.objects.get(user=self.user)
        profile.avatar.delete(save=False)
        super().tearDown()

    def test_user_profile_creation(self):
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get(user=self.user).user, self.user)
        self.assertEqual(str(Profile.objects.get(user=self.user)), self.user.username)

    def test_save_without_avatar(self):
        profile = Profile.objects.get(user=self.user)
        profile.save()
        self.assertFalse(profile.avatar)

    def test_save_with_small_avatar(self):
        img = Image.new("RGB", (50, 50), color="red")
        file = BytesIO()
        img.save(file, "jpeg")
        file.seek(0)

        profile = Profile.objects.get(user=self.user)
        profile.avatar.save("avatar.jpeg", file, save=True)
        profile.save()

        # Check that the avatar was not resized
        with Image.open(profile.avatar.path) as img:
            self.assertEqual(img.size, (50, 50))

    def test_save_with_large_avatar(self):
        img = Image.new("RGB", (200, 200), color="red")
        file = BytesIO()
        img.save(file, "jpeg")
        file.seek(0)

        profile = Profile.objects.get(user=self.user)
        profile.avatar.save("avatar.jpeg", file, save=True)
        profile.save()

        # Check that the avatar was resized
        with Image.open(profile.avatar.path) as img:
            self.assertEqual(img.size, (100, 100))


from django.core.files.uploadedfile import SimpleUploadedFile, TemporaryUploadedFile
from django.test import Client
from rest_framework import status
from rest_framework.reverse import reverse

from config.tests import GlobalTestSetup, inject_token

from utils.b64 import file_to_base64


class UserListViewTestCase(GlobalTestSetup):
    def setUp(self):
        super().setUp("user-list")
        self.create_user_data = {
            "user": {
                "username": "test_user2",
                "password": "test_password2",
                "email": "test2@test2.com",
            },
            "bio": "Test bio",
            "location": "Test location",
            "birth_date": "2000-01-01",
        }
        self.user.profile.bio = "Test bio"
        self.user.profile.location = "Test location"
        self.user.profile.birth_date = "2000-01-01"
        self.user.profile.save()

    def test_list_users(self):
        inject_token(self.client)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"]["username"], self.user.username)
        self.assertEqual(response.data[0]["bio"], self.user.profile.bio)
        self.assertEqual(response.data[0]["location"], self.user.profile.location)
        self.assertEqual(response.data[0]["birth_date"], self.user.profile.birth_date)

    def test_list_users_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_creation(self):
        inject_token(self.client)

        response = self.client.post(self.url, self.create_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["username"], self.create_user_data["user"]["username"])
        self.assertEqual(response.data["bio"], self.create_user_data["bio"])
        self.assertEqual(response.data["location"], self.create_user_data["location"])
        self.assertEqual(response.data["birth_date"], self.create_user_data["birth_date"])

    def test_user_creation_without_authentication(self):
        response = self.client.post(self.url, self.create_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_creation_without_authorization(self):
        inject_token(self.client)
        self.user.is_staff = False
        self.user.save()

        response = self.client.post(self.url, self.create_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_new_user_added_to_list(self):
        inject_token(self.client)
        response = self.client.post(self.url, self.create_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_creation_with_invalid_data(self):
        inject_token(self.client)
        self.create_user_data["user"]["username"] = ""
        response = self.client.post(self.url, self.create_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"]["username"][0], "This field may not be blank.")

    def test_user_creation_with_existing_username(self):
        inject_token(self.client)
        self.create_user_data["user"]["username"] = self.user.username
        response = self.client.post(self.url, self.create_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["detail"], "User already exists")


class UserDetailViewTestCase(GlobalTestSetup):
    def setUp(self):
        super().setUp("user-detail", {"pk": 2})

        self.new_user = User.objects.create_user(
            username="test_user2",
            password="test_password2",
            email="test2@test2.com",
        )
        self.new_user.profile.bio = "Test bio"
        self.new_user.profile.location = "Test location"
        self.new_user.profile.birth_date = "2000-01-01"
        self.new_user.profile.save()

        self.update_user_data = {
            "bio": "Test bio 2",
            "location": "Test location 2",
            "birth_date": "2000-02-02",
        }

    def tearDown(self):
        if Profile.objects.filter(user=self.new_user).exists():
            profile = Profile.objects.get(user=self.new_user)
            if profile.avatar:
                profile.avatar.delete(save=False)
        super().tearDown()

    def test_get_user(self):
        inject_token(self.client)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["username"], self.new_user.username)
        self.assertEqual(response.data["bio"], self.new_user.profile.bio)
        self.assertEqual(response.data["location"], self.new_user.profile.location)
        self.assertEqual(response.data["birth_date"], self.new_user.profile.birth_date)

    def test_check_base64_avatar(self):
        inject_token(self.client)
        self.new_user.profile.avatar = SimpleUploadedFile(
            name="test_image.jpg",
            content=open("media/profile_avatars/test_avatar_64.jpg", "rb").read(),
            content_type="image/jpg",
        )
        self.new_user.profile.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["avatar_base64"], file_to_base64(self.new_user.profile.avatar))

    def test_get_user_with_invalid_pk(self):
        inject_token(self.client)
        self.url = reverse("user-detail", kwargs={"pk": 3})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user(self):
        inject_token(self.client)
        response = self.client.patch(self.url, self.update_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], self.update_user_data["bio"])
        self.assertEqual(response.data["location"], self.update_user_data["location"])
        self.assertEqual(response.data["birth_date"], self.update_user_data["birth_date"])

    def test_update_user_with_avatar(self):
        inject_token(self.client)

        self.update_user_data[
            "avatar"
        ] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="
        response = self.client.patch(self.url, self.update_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], self.update_user_data["bio"])
        self.assertEqual(response.data["location"], self.update_user_data["location"])
        self.assertEqual(response.data["birth_date"], self.update_user_data["birth_date"])
        self.assertEqual(response.data["avatar"], "http://testserver/media/profile_avatars/image.png")

    def test_update_user_with_invalid_pk(self):
        inject_token(self.client)
        self.url = reverse("user-detail", kwargs={"pk": 3})
        response = self.client.patch(self.url, self.update_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_without_authentication(self):
        response = self.client.patch(self.url, self.update_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_without_authorization(self):
        inject_token(self.client)
        self.user.is_staff = False
        self.user.save()

        response = self.client.patch(self.url, self.update_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user(self):
        inject_token(self.client)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_myself(self):
        inject_token(self.client)
        self.url = reverse("user-detail", kwargs={"pk": 1})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You cannot delete yourself")

    def test_delete_user_without_authentication(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_without_authorization(self):
        inject_token(self.client)
        self.user.is_staff = False
        self.user.save()

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_with_invalid_pk(self):
        inject_token(self.client)
        self.url = reverse("user-detail", kwargs={"pk": 3})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UploadAvatarViewTest(GlobalTestSetup):
    def setUp(self):
        super().setUp(url="upload-avatar", url_kwargs={"pk": 1})
        self.avatar = SimpleUploadedFile(
            name="image.png",
            content=open("media/profile_avatars/test_avatar.jpg", "rb").read(),
            content_type="image/jpg",
        )

    def tearDown(self) -> None:
        profile = Profile.objects.get(user=self.user)
        if profile.avatar:
            profile.avatar.delete(save=False)
        super().tearDown()

    def test_upload_avatar(self):
        inject_token(self.client)
        response = self.client.patch(self.url, {"avatar": self.avatar}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["avatar"], "http://testserver/media/profile_avatars/image.png")

    def test_upload_avatar_with_invalid_pk(self):
        inject_token(self.client)
        self.url = reverse("upload-avatar", kwargs={"pk": 3})
        response = self.client.patch(self.url, {"avatar": self.avatar}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upload_avatar_without_authentication(self):
        response = self.client.patch(self.url, {"avatar": self.avatar}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_avatar_without_authorization(self):
        inject_token(self.client)
        self.user.is_staff = False
        self.user.save()

        response = self.client.patch(self.url, {"avatar": self.avatar}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_avatar_with_invalid_avatar(self):
        inject_token(self.client)
        response = self.client.patch(self.url, {"avatar": "invalid_avatar"}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
