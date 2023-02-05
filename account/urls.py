from django.urls import path

from account.views import (
    RegisterView,
    GetCurrentUserView,
    ChangePasswordView,
    LoginView,
    RefreshTokenView,
    ForgotPasswordView,
    SetPasswordView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh-token"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", GetCurrentUserView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("set-password/", SetPasswordView.as_view(), name="set-password"),
]
