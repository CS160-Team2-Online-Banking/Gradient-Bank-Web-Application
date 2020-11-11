from django.urls import path, re_path
from . import views

app_name = 'transaction'
urlpatterns = [
    path('autopayments', views.transaction, name='transaction'),
    re_path(r'^transfers(?P<type>/((internal)|(external)))$', views.transfer, name='transfer')
]
