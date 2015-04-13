from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from miau.backend.django import subscriptable
User = get_user_model()


@subscriptable
class Issue(models.Model):
    initiator = models.ForeignKey(User, related_name='reported_issues')
    title = models.CharField(max_length=150)
    date = models.DateTimeField(auto_now_add=True)
    solved = models.BooleanField(default=False)
    content = models.TextField()
    needs_attention = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title

    def jsonify(self):
        from .serializers import IssueSerializer
        return IssueSerializer(self).data

    class Meta:
        permissions = (
            ('manage_issues', "Can list and view all issues"),
        )


@subscriptable
class IssueReply(models.Model):
    author = models.ForeignKey(User, related_name='issue_replies')
    issue = models.ForeignKey('Issue', related_name='replies')
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    ACTION_CHOICES = (
        ('none', 'None'),
        ('close', 'Close'),
        ('reopen', 'Reopen'),
    )
    action = models.CharField(max_length=8, choices=ACTION_CHOICES,
                              default='none')

    def __unicode__(self):
        return self.content[:50]

    def jsonify(self):
        from .serializers import IssueReplySerializer
        return IssueReplySerializer(self).data

    class Meta:
        index_together = [
            ['issue', 'date'],
        ]
        verbose_name_plural = "Issue replies"
        permissions = (
            ('reply_all', "Can reply any issues"),
        )


@receiver(post_save, sender=IssueReply)
def update_issue(sender, instance, created, **kwargs):
    if created:
        issue = instance.issue

        # The issue needs attention if feedback is given from the one who
        # opened it.
        if instance.author == issue.initiator:
            issue.needs_attention = True
        # The issue does no longer require attention if other people (from the
        # support team) replies it
        else:
            issue.needs_attention = False

        # Close or reopen if requested
        if instance.action == 'close':
            issue.solved = True
        elif instance.action == 'reopen':
            issue.solved = False

        issue.save()
