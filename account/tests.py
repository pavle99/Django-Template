from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

from config.tests import GlobalTestSetup, inject_token, login_url, valid_credentials, invalid_credentials

from utils.mail import send_set_password_email

refresh_token_url = reverse("refresh-token")
register_url = reverse("register")
get_current_user_url = reverse("me")
change_password_url = reverse("change-password")
forgot_password_url = reverse("forgot-password")
set_password_url = reverse("set-password")


class LoginViewTestCase(GlobalTestSetup):
    def test_login_with_valid_credentials(self):
        response = self.client.post(login_url, valid_credentials, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(login_url, invalid_credentials, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid credentials!")


class RefreshTokenViewTestCase(GlobalTestSetup):
    def test_refresh_token_with_valid_credentials(self):
        login_response = self.client.post(login_url, valid_credentials, format="json")

        refresh_token = login_response.data["refresh_token"]
        response = self.client.post(refresh_token_url, {"refresh_token": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    def test_refresh_token_with_invalid_credentials(self):
        refresh_token = "wrong_refresh_token"
        response = self.client.post(refresh_token_url, {"refresh_token": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Token is invalid or expired")


class RegisterViewTestCase(GlobalTestSetup):
    def setUp(self):
        super().setUp()
        self.data = {
            "username": "new_user",
            "password": "new_password",
            "email": "new@new.com",
            "first_name": "new",
            "last_name": "user",
        }
        self.existing_data = {
            "username": "test_user",
            "password": "test_password",
            "email": "test@test.com",
            "first_name": "test",
            "last_name": "user",
        }

    def test_register(self):
        response = self.client.post(register_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username="new_user").username, "new_user")

    def test_register_with_existing_username(self):
        response = self.client.post(register_url, self.existing_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["detail"], "User already exists")


class GetCurrentUserViewTestCase(GlobalTestSetup):
    def test_get_current_user(self):
        inject_token(self.client)
        response = self.client.get(get_current_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "test_user")

    def test_get_current_user_without_authentication(self):
        response = self.client.get(get_current_user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")


class ChangePasswordViewTestCase(GlobalTestSetup):
    def setUp(self):
        super().setUp()
        self.data = {"old_password": "test_password", "new_password": "new_password"}

    def test_change_password(self):
        inject_token(self.client)
        response = self.client.patch(change_password_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password changed successfully")

    def test_change_password_with_invalid_old_password(self):
        inject_token(self.client)
        self.data["old_password"] = "invalid_password"
        response = self.client.patch(change_password_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Old password is incorrect")

    def test_change_password_without_authentication(self):
        response = self.client.patch(change_password_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")


class ForgotPasswordViewTestCase(GlobalTestSetup):
    def test_forgot_password_email_sent(self):
        response = self.client.post(forgot_password_url, {"email": self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Email sent successfully")

    def test_user_not_found(self):
        response = self.client.post(forgot_password_url, {"email": "notfound@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "User not found")

    def test_send_set_password_email(self):
        send_set_password_email(self.user)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, "Set Password")
        self.assertEqual(mail.outbox[0].from_email, "from@example.com")
        self.assertEqual(mail.outbox[0].to, [self.user.email])


class SetPasswordViewTestCase(GlobalTestSetup):
    def setUp(self):
        super().setUp()
        self.token = default_token_generator.make_token(self.user)

    def test_set_password(self):
        response = self.client.patch(
            set_password_url, {"token": self.token, "new_password": "new_password", "email": self.user.email}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password set successfully")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password"))

    def test_set_password_with_invalid_token(self):
        response = self.client.patch(
            set_password_url, {"token": "invalid_token", "new_password": "new_password", "email": self.user.email}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid token")
