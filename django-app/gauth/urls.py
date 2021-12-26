from django.urls import path
from . import views

urlpatterns = [
    path('gmailAuthenticate', views.gmail_authenticate, name='gmail_authenticate'),
    path('oauth2callback', views.auth_return),
    path('list', views.list, name='list'),
    path('credentials', views.credentials, name='credentials'),
    path('refresh', views.refresh, name='refresh'),
    path('', views.home, name='home'),
]
