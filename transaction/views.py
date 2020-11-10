from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *


class Transaction(View):
    def get(self, request, *args, **kwargs):
        result = []
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request.user)
            if not from_accounts:
                from_accounts = []
        return render(request, 'transaction/transaction.html', {"from_accounts": from_accounts})

    def post(self, request):
        pass  # here is where you retrieve the form data and post the transfer


transaction = Transaction.as_view()
