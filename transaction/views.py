from django.shortcuts import render
from django.views import View


class Transaction(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'transaction/transaction.html')


transaction = Transaction.as_view()
