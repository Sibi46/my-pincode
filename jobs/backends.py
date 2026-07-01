from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneOrEmailBackend(ModelBackend):
    """Allow login with phone number or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        for user in User.objects.filter(phone=username):
            if user.check_password(password):
                return user
        for user in User.objects.filter(email=username):
            if user.check_password(password):
                return user
        return None
