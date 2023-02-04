from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from config import settings


def send_set_password_email(user):
    token = default_token_generator.make_token(user)
    set_password_url = settings.FRONTEND_URL + "?token=" + token + "&email=" + user.email
    context = {
        'user': user,
        "set_password_url": set_password_url,
    }
    message = render_to_string('set_password.html', context)

    email = EmailMessage(
        subject='Set Password',
        body=message,
        from_email='from@example.com',
        to=[user.email],
    )
    email.content_subtype = "html"
    email.send()
