from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from .patch_view_decorator import login_required, permission_required
from . import forms
from . import models
from .util import unnamed_user
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
User = get_user_model()


class Home(FormView):
    template_name = 'helpdesk/index.html'
    form_class = forms.LoginForm

    def get_context_data(self, **kwargs):
        host = self.request.META['HTTP_HOST']
        # Choose the first different domain
        other_domain = [x for x in settings.ALTERNATIVE_DOMAINS
                        if x != host][0]
        return {'other_domain': other_domain}

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return super(Home, self).get(request, *args, **kwargs)
        else:
            return self.redirect_logged()

    def form_valid(self, form):
        if form.cleaned_data['admin']:
            email = 'admin@snorkyproject.org'
            user, _ = User.objects.get_or_create(
                username=email,
                email=email,
                is_staff=True,
                is_superuser=True)
        else:
            email = form.cleaned_data['email']
            user, _ = User.objects.get_or_create(
                username=email, email=email)
        user = authenticate(username=user.username)

        login(self.request, user)
        return HttpResponseRedirect('/')

    def redirect_logged(self):
        if unnamed_user(self.request.user):
            return redirect('my_data')

        if self.request.user.has_perm('helpdesk.manage_issues'):
            return redirect('all_issues')
        else:
            return redirect('my_issues')


@login_required
class LogOut(View):
    def post(self, request):
        logout(request)
        return HttpResponseRedirect('/')

@login_required
class MyData(UpdateView):
    model = User
    template_name = 'helpdesk/my_data.html'
    fields = ['first_name', 'last_name']
    success_url = '/'

    def get_object(self):
        return self.request.user


@login_required
class PostIssue(CreateView):
    form_class = forms.PostIssueForm
    template_name = 'helpdesk/post_issue.html'

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.initiator = self.request.user
        issue.save()

        return redirect('view_issue', pk=issue.id)


@permission_required('helpdesk.manage_issues')
class AllIssues(TemplateView):
    template_name = 'helpdesk/all_issues.html'


@login_required
class MyIssues(TemplateView):
    template_name = 'helpdesk/my_issues.html'


@login_required
class ViewIssue(TemplateView):
    form_class = forms.ReplyIssueForm
    template_name = 'helpdesk/view_issue.html'

    def get_context_data(self, **kwargs):
        kwargs = super(ViewIssue, self).get_context_data(**kwargs)
        kwargs['issue'] = get_object_or_404(models.Issue, pk=self.kwargs['pk'])
        return kwargs
