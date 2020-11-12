from django.shortcuts import render
from django.views import View
from .utils import request_api


class Transaction(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'transaction/transaction.html')

    def post(self, request, *args, **kwargs):

        form_values = [
            self.request.POST.get('accounts', None),
            self.request.POST.get('bills', None),
            self.request.POST.get('amount', None),
            self.request.POST.get('auto_payment_date', None),
        ]
        print(form_values)
        return render(request, 'transaction/transaction.html')


transaction = Transaction.as_view()
