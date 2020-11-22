from django.urls import path
from . import views

app_name = 'autopayment'
urlpatterns = [
    path('details/<int:autopayment_id>',
         views.AutopaymentDetails, name='autopaymentdetails'),
    path('delete/<int:autopayment_id>',
         views.AutopaymentDelete, name='autopaymentdelete')
]
