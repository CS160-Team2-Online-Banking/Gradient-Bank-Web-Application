from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from django import forms
from accounts.models import BankManagerUser


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
        return render(request, "managerportal/landing.html", {"manager": manager})

    def post(self, request):
        pass

