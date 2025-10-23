from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from news.models import Author


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    def get_context_data_c(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_common'] = not self.request.user.groups.filter(name='common').exists()
        return context

@login_required
def upgrade_me(request):
    if not hasattr(request.user, 'author'):
        Author.objects.create(author_user=request.user)
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(request.user)
    return redirect('/info/my/')

@login_required
def upgrade_common(request):
    user = request.user
    premium_group = Group.objects.get(name='common')
    if not request.user.groups.filter(name='common').exists():
        premium_group.user_set.add(user)
    return redirect('/info/my/')