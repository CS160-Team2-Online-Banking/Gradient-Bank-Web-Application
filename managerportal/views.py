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


class LandingView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        manager = get_manager(user)
        start_date = datetime.utcnow() - timedelta(days=60)
        end_date = datetime.utcnow()
        result = api_get_data(user, manager, "get_income", {"customer_id":4, "time_delta":"WEEK"})
        print(result)
        return render(request, "managerportal/landing.html", {"manager": manager})

    def post(self, request):
        pass

