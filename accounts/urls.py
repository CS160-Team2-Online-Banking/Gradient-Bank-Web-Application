from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/',
         SignInView.as_view(), name='login'),
    path('customer/login',
         CustomerSignIn.as_view(), name='cus_login'),
    re_path(r'customer/edit/(?P<pk>\d+)/$',
         CustomerUpdateView.as_view(), name='cus_edit'),
    path('employee/login',
         EmployerSignIn.as_view(), name='emp_login'),
    path('logout/',
         LogOut.as_view(), name='logout'),
    path('signup/',
         CustomerSignUp.as_view(), name='signup'),  # this should direct you to a customer sign up
    path('customer/close', CustomerCloseView.as_view(), name='cus_close')
]
