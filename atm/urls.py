from django.urls import path
from . import atm_detail_views, atm_list_views


app_name = 'atm'

urlpatterns = [
    path('search/', atm_list_views.atm_list, name='atm_list'),
    path('detail/<int:atm_id>', atm_detail_views.atm_detail, name='atm_detail'),
]
