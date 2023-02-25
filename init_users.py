from django.contrib.auth.models import User


def init_users():
    # Delete all existing users
    User.objects.all().delete()

    # Create regular user
    regular_user = User.objects.create_user(
        username="regular_user@test.com",
        email="regular_user@test.com",
        password="testtest",
        first_name="Regular",
        last_name="User",
    )
    regular_user.save()

    # Create a new staff user
    staff_user = User.objects.create_user(
        username="staff_user@test.com",
        email="staff_user@test.com",
        password="testtest",
        first_name="Staff",
        last_name="User",
        is_staff=True,
    )
    staff_user.save()
