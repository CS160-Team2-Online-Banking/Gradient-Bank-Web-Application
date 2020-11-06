from django.urls import include, path
from bankapi.views import TransferView, AutoPaymentView, TransactionView

urlpatterns = [
    path('transfers', TransferView.as_view()),
    # path('authentication', AuthView.as_view()),
    path('autopayments', AutoPaymentView.as_post_view()),
    path('autopayments/<int:autopayment_id>', AutoPaymentView.as_access_view()),
    path('transaction', TransactionView.as_view())
]