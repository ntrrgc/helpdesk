from django.contrib.auth import get_user_model
User = get_user_model()

def create_user(email):
    user = User(username=email, email=email)
    user.first_name = "Anonymous"
    user.last_name = "Surname"
    user.save()
    return user

def unnamed_user(user):
    return user.get_full_name() == "Anonymous Surname"
