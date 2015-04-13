from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('', include('helpdesk.urls')),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
