from django.forms import Form, ModelForm, EmailField, HiddenInput, BooleanField
from . import models
from django.contrib.auth import get_user_model
User = get_user_model()


class PostIssueForm(ModelForm):
    class Meta:
        model = models.Issue
        fields = ['title', 'content']


class ReplyIssueForm(ModelForm):
    class Meta:
        model = models.IssueReply
        fields = ['content']


class LoginForm(Form):
    email = EmailField(label="Email", required=False)
    admin = BooleanField(widget=HiddenInput, required=False)
