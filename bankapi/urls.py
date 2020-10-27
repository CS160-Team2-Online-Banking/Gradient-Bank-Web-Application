from django.urls import include, path
from bankapi.views import TransferView, AuthView

urlpatterns = [
    path('transfers', TransferView.as_view()),
    path('authentication', AuthView.as_view())
]