from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

login_url = reverse("login")

valid_credentials = {"username": "test_user", "password": "test_password"}
invalid_credentials = {"username": "test_user", "password": "invalid_password"}


def inject_token(client):
    login_response = client.post(login_url, valid_credentials, format="json")

    access_token = login_response.data["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


class GlobalTestSetup(TestCase):
    def setUp(self, url: str = None, url_kwargs: dict = None):
        self.client = APIClient()

        self.user = User.objects.create_user(username="test_user", password="test_password", email="test@test.com")
        self.user.is_staff = True
        self.user.save()

        if url:
            self.url = reverse(url, kwargs=url_kwargs)
