from django.contrib.auth import get_user_model
User = get_user_model()

def create_user(email):
    user, _ = User.objects.get_or_create(
        username=email,
        email=email,
        first_name="Anonymous",
        last_name="Surname")
    return user

def unnamed_user(user):
    return user.get_full_name() == "Anonymous Surname"
