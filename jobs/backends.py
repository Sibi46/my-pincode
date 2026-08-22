from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

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
        for user in User.objects.filter(username=username):
            if user.check_password(password):
                return user
        return None


class FamilyAccountBackend(ModelBackend):
    """Allow login with family account email+password (stored on FamilySetup)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        try:
            from community.models import FamilySetup, FamilyMember
            # Try primary family account email
            setup = FamilySetup.objects.select_related('user').get(
                family_email__iexact=username.strip()
            )
            if setup.family_password and check_password(password, setup.family_password):
                return setup.user
        except Exception:
            pass

        try:
            from community.models import FamilyMember
            # Try child 18+ account
            member = FamilyMember.objects.select_related('child_linked_user').get(
                child_email__iexact=username.strip(),
                child_linked_user__isnull=False,
            )
            if member.child_password and check_password(password, member.child_password):
                return member.child_linked_user
        except Exception:
            pass

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
