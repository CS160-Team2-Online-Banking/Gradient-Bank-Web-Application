from django.urls import include, path
from bankapi.views import TransferView

urlpatterns = [path('transfers/<int:id>', TransferView.as_view())]