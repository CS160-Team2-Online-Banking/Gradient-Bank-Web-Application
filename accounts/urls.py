from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from .signup_views import *

app_name = 'accounts'

urlpatterns = [
    path('customer/login/',
         TemplateView.as_view(template_name='login.html'), name='login'),
    path('logout/',
         TemplateView.as_view(template_name='logout.html'), name='logout'),
    path('customer/signup/',
         CustomerSignUp.as_view(), name='signup'),  # this should direct you to a customer sign up
]
