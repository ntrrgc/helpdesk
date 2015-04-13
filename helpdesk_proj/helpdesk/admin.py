from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Issue)
admin.site.register(models.IssueReply)
