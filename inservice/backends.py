from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailPhoneUsernameAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
    
        try:
            user = User.objects.get(
                Q(mobile=username) | Q(email=username)
            )
            # return user
        except User.DoesNotExist:
            return None

        if user and check_password(password, user.password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None