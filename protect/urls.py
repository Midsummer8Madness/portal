from django.urls import path
from .views import IndexView
from .views import upgrade_me, upgrade_common

urlpatterns = [
    path('my/', IndexView.as_view()),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('upgrade_common/', upgrade_common, name='upgrade')
]