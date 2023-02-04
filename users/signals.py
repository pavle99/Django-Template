from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.mail import send_set_password_email
from users.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Profile)
def send_email_on_profile_creation(sender, instance, created, **kwargs):
    if created:
        send_set_password_email(instance.user)