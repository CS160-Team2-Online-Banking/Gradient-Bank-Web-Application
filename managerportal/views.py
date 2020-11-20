from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from django import forms
from accounts.models import BankManagerUser
from .requests import api_get_data
from datetime import datetime


class OpenAccountForm(forms.Form):
    account_type = forms.ChoiceField(choices=[("SAVING", "Savings Account"), ("CHECKING", "Checking Account")])


def get_manager(user):
    if user.is_authenticated:
        return BankManagerUser.objects.filter(pk=user.pk).first()
    return None


def set_or_message(result, key, dict, mapper=lambda x: x):
    if result:
        dict[key] = mapper(result)
    else:
        dict[key] = "#ERROR"


class LandingView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        manager = get_manager(user)
        """
        start_date = datetime.utcnow() - timedelta(days=60)
        end_date = datetime.utcnow()
        result = api_get_data(user, manager, "get_income", {"customer_id": 4, "time_delta": "WEEK"})
        print(result)
        """
        headline = {}
        set_or_message(api_get_data(user, manager, "get_customer_count", {}), "customer_count", headline, lambda x: list(x.values())[0])
        set_or_message(api_get_data(user, manager, "get_exchange_count", {}), "exchange_count", headline, lambda x: list(x.values())[0])
        set_or_message(api_get_data(user, manager, "get_failed_transactions", {}), "failed_exchanges", headline, lambda x: list(x.values())[0])
        set_or_message(api_get_data(user, manager, "get_total_savings", {}), "total_balance", headline, lambda x: list(x.values())[0])

        return render(request, "managerportal/landing.html", {"manager": manager, "headline":headline})

    def post(self, request):
        pass

