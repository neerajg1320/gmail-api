from django.urls import path
from . import views

urlpatterns = [
    path('gmailAuthenticate', views.gmail_authenticate, name='gmail_authenticate'),
    path('oauth2callback', views.auth_return),
    path('list', views.list, name='list'),
    path('', views.home, name='home'),
]
