from . import models, serializers, permissions
from rest_framework import mixins, viewsets, generics
from rest_framework import status
from rest_framework.response import Response
import snorky.backend.django.rest_framework as snorky


class ListIssuesView(snorky.ListSubscribeAPIView):
    serializer_class = serializers.IssueSerializer
    permission_classes = [permissions.ManipulateIssuesPermission]
    model = models.Issue
    dealer = 'AllIssues'


class MyIssuesView(snorky.ListSubscribeAPIView):
    serializer_class = serializers.IssueSerializer
    dealer = 'IssuesByUser'
    model = models.Issue

    def get_dealer_query(self):
        return self.request.user.email

    def get_queryset(self):
        return models.Issue.objects.filter(initiator=self.request.user)


class RetrieveIssueView(snorky.SubscribeModelMixin,
                        generics.RetrieveAPIView):
    serializer_class = serializers.IssueWithRepliesSerializer
    model = models.Issue
    permission_classes = [permissions.ManagerOrInitiator]

    def get_subscription_items(self):
        issue_id = int(self.kwargs['pk'])
        return [{ 'dealer': 'Issue',
                  'query': issue_id },
                { 'dealer': 'IssueReplies',
                  'query': issue_id }]

    @snorky.subscription_in_response
    def retrieve(self, *args, **kwargs):
        return super(RetrieveIssueView, self).retrieve(*args, **kwargs)


class ReplyToIssue(generics.CreateAPIView):
    serializer_class = serializers.NewIssueReplySerializer
    permission_classes = [permissions.ManagerOrInitiator]
    model = models.IssueReply

    def pre_save(self, obj):
        super(ReplyToIssue, self).pre_save(obj)
        obj.author = self.request.user
