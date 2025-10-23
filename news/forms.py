from django import forms
from .models import Post, Category
import django_filters

class PostForm(forms.ModelForm):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Название')
    text = django_filters.CharFilter(field_name='text', lookup_expr='icontains', label='Текст')
    postCategory = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Post
        fields = ['categoryType', 'title', 'text', 'postCategory']
