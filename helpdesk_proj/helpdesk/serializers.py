from . import models
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email')


class IssueSerializer(serializers.ModelSerializer):
    initiator = UserSerializer()
    date = serializers.DateTimeField()

    class Meta:
        model = models.Issue
        fields = ('id', 'initiator', 'title', 'solved', 'content', 'date',
                  'needs_attention')


class IssueReplySerializer(serializers.ModelSerializer):
    author = UserSerializer()
    issue_id = serializers.IntegerField(source='issue.id')
    date = serializers.DateTimeField()

    class Meta:
        model = models.IssueReply
        fields = ('id', 'issue_id', 'author', 'date', 'content', 'action')


class IssueWithRepliesSerializer(IssueSerializer):
    replies = IssueReplySerializer()

    class Meta(IssueSerializer.Meta):
        fields = IssueSerializer.Meta.fields + ('replies',)


class NewIssueReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IssueReply
        fields = ('issue', 'content', 'action')
