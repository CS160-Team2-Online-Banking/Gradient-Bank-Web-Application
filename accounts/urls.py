from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

app_name = 'accounts'

urlpatterns = [
    path('accounts/login/',
         TemplateView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/',
         TemplateView.as_view(template_name='logout.html'), name='logout'),
    path('accounts/signup/',
         TemplateView.as_view(template_name='signup.html'), name='signup'),
]
