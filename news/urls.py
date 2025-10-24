from django.urls import path
# Импортируем созданное нами представление
from .views import (PostList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch,
                    NewsCreateView, NewsUpdateView, ArticleCreateView, ArticleUpdateView,
                    SubscribeCategoryView, UnsubscribeCategoryView)


urlpatterns = [
    path('', PostList.as_view(), name='post'),
    path('<int:pk>/', PostDetail.as_view(), name='post_read'),


    path('news/search/', PostSearch.as_view(), name='post_search'),
    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),

    path('articles/create/', ArticleCreateView.as_view(), name='articles_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='articles_edit'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),

    path('<int:pk>/subscribe/', SubscribeCategoryView.as_view(), name='subscribe_category'),
    path('<int:pk>/unsubscribe/', UnsubscribeCategoryView.as_view(), name='unsubscribe_category'),
]