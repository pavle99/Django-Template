from django.urls import path

from users.views import UserListView, UserDetailView, UploadAvatarView, InitializeUsersView

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:pk>/upload-avatar/", UploadAvatarView.as_view(), name="upload-avatar"),
    path("initialize-users/", InitializeUsersView.as_view(), name="initialize-users"),
]
