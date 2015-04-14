from django.conf.urls import patterns, include, url
from rest_framework import routers, viewsets, mixins
from . import views, api, models, serializers

class IssuesViewSet(viewsets.ViewSet):
    def list(self, request):
        return api.ListIssuesView.as_view()(request)

    def retrieve(self, request, pk=None):
        return api.RetrieveIssueView.as_view()(request, pk=pk)


class MyIssuesViewSet(viewsets.ModelViewSet):
    def list(self, request):
        return api.MyIssuesView.as_view()(request)


router = routers.DefaultRouter(trailing_slash=False)
router.register("issues", IssuesViewSet, base_name="issue")
router.register("my-issues", MyIssuesViewSet, base_name="my-issues")

urlpatterns = patterns('',
    url(r'^$', views.Home.as_view(), name='login'),
    url(r'^logout/$', views.LogOut.as_view(), name='logout'),
    url(r'^issues/new/$', views.PostIssue.as_view(), name='post_issue'),
    url(r'^issues/(?P<pk>\d+)/$', views.ViewIssue.as_view(),
        name='view_issue'),
    url(r'^issues/$', views.AllIssues.as_view(), name='all_issues'),
    url(r'^my-issues/$', views.MyIssues.as_view(), name='my_issues'),
    url(r'^my-data/$', views.MyData.as_view(), name='my_data'),

    url("^api/", include(router.urls)),

    url(r'^api/$', 'django.views.defaults.page_not_found', name='api-root'),
    url(r'^api/issues/(?P<pk>\d+)$', api.RetrieveIssueView.as_view()),
    url(r'^api/replies$', api.ReplyToIssue.as_view()),
)
