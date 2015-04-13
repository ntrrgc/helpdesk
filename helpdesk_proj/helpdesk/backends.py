from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class NullAuthBackend(ModelBackend):
    def authenticate(self, username=None):
        User = get_user_model()
        return User.objects.get(email=username)
