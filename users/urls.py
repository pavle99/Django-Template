from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from users.views import UserListView, UserDetailView, UploadAvatarView

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:pk>/upload-avatar/", UploadAvatarView.as_view(), name="upload-avatar"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
