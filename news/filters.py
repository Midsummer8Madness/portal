from django.forms.widgets import DateInput
import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Название')
    author = django_filters.CharFilter(field_name='author_user', lookup_expr='icontains', label='Автор')
    dateCreation = django_filters.DateFilter(
        field_name='dateCreation',
        lookup_expr='gte',
        widget=DateInput(attrs={'type': 'date'}),
        label='Дата'
    )

    class Meta:
        model = Post
        fields = ['title', 'author', 'dateCreation']