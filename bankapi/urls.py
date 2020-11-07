from django.urls import include, path, re_path
from bankapi.views import TransferView, AutoPaymentView, TransactionView, AuthView

urlpatterns = [
    path('transfers', TransferView.as_view()),
    path('authentication', AuthView.as_view()),
    path('autopayments', AutoPaymentView.as_post_view()),
    re_path(r'^autopayments/(?P<autopayment_id>[0-9]+)?', AutoPaymentView.as_access_view()),
    path('transaction', TransactionView.as_view())
]