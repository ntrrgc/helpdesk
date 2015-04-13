from rest_framework.permissions import BasePermission
from . import models


class ManagerOrInitiator(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        The action on a Issue or IssueReply object is allowed if the requester
        is either an authorized manager or if they are the initiator of the
        issue.
        """
        if isinstance(obj, models.Issue):
            initiator = obj.initiator
        elif isinstance(obj, models.IssueReply):
            initiator = obj.issue.initiator
        else:
            raise RuntimeError("Permission used on invalid object")

        if initiator == request.user:
            return True
        elif request.user.has_perm('helpdesk.manage_issues'):
            return True
        else:
            return False


class ManipulateIssuesPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('helpdesk.manage_issues')
