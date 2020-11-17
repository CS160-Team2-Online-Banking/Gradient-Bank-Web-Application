from django.urls import path
from . import views

app_name = 'bankaccount'
urlpatterns = [
    path('', views.OpenAccount, name='bankaccount'),
    path('details/<int:account_no>', views.AccountDetails, name='accountdetails')
]
