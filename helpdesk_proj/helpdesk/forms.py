from django.forms import ModelForm
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
