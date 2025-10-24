from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Category, Author
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.core.mail import send_mail
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import mail_admins
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views.generic.edit import CreateView

def posts_last_24_hours(author):
    time_threshold = timezone.now() - timedelta(days=1)
    return Post.objects.filter(author=author, dateCreation__gte=time_threshold).count()

class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post')
    template_name = 'news/post_edit.html'

    def form_valid(self, form):
        # Получаем текущего автора
        try:
            author = Author.objects.get(author_user=self.request.user)
        except Author.DoesNotExist:
            return HttpResponseForbidden("Автор не найден.")

        # Проверка лимита публикаций за последние 24 часа
        if posts_last_24_hours(author) >= 100:
            messages.error(self.request, 'Вы не можете публиковать более 3 новостей в сутки.')
            return self.form_invalid(form)

        # Связываем автора с постом
        form.instance.author = author

        # Сохраняем пост
        post = form.save()

        # Проверяем, что категории правильно передаются
        categories = form.cleaned_data.get('postCategory')
        if categories:
            print(f"Категории для поста: {categories}")  # Отладка: выводим категории
            post.postCategory.set(categories)  # Устанавливаем связи сразу
            post.save()  # Перезаписываем пост с связями
            print(
                f"Связи с категориями установлены. Количество категорий: {post.postCategory.count()}")  # Проверка связи
        else:
            print("Категории не были выбраны.")  # Если категории не были выбраны

        return redirect(self.success_url)

    def test_func(self):
        # Проверка, что пользователь в группе 'authors'
        return self.request.user.groups.filter(name='authors').exists()

class SubscribeCategoryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.subscribers.add(request.user)
        return render(request, 'news/subscribe.html', {
            'user': request.user,
            'subscribed': category,
        })

class UnsubscribeCategoryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.subscribers.remove(request.user)
        return render(request, 'unsubscribe.html', {
            'user': request.user,
            'unsubscribed': category,
        })

class PostList(ListView):
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10 # вот так мы можем указать количество записей на странице

    def get_queryset(self):
       queryset = super().get_queryset()
       self.filterset = PostFilter(self.request.GET, queryset)
       return self.filterset.qs

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['filterset'] = self.filterset
       context['categories'] = Category.objects.all()
       return context

class PostDetail(DetailView):
    model = Post
    template_name = 'news/post_read.html'
    context_object_name = 'post_read'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user
        try:
            author = user.author
        except Author.DoesNotExist:
            author = None
        context['is_authors'] = (author == post.author)
        return context

class PostDelete(DeleteView):
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('post')

class PostSearch(ListView):
    model = Post
    template_name = 'news/post_search.html'
    context_object_name = 'post_search'
    paginate_by = 10  # по желанию

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['categories'] = Category.objects.all()
        return context

class NewsCreateView(PostCreate):
    def form_valid(self, form):
        form.instance.categoryType = 'NW'
        return super().form_valid(form)
success_url = "{% url 'post_read' post_read.pk %}"

class ArticleCreateView(PostCreate):
    def form_valid(self, form):
        form.instance.categoryType = 'AR'
        return super().form_valid(form)

class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'news/post_edit.html'
    success_url = reverse_lazy('post')

    def form_valid(self, form):
        try:
            author = self.request.user.author
            form.instance.author = author
        except Author.DoesNotExist:
            return self.handle_no_permission()
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        user = self.request.user
        try:
            author = user.author
        except Author.DoesNotExist:
            return False
        return post.author == author

class NewsUpdateView(PostUpdate):
    def form_valid(self, form):
        form.instance.categoryType = 'NW'
        return super().form_valid(form)

class ArticleUpdateView(PostUpdate):
    def form_valid(self, form):
        form.instance.categoryType = 'AR'
        return super().form_valid(form)