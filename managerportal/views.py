from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from django import forms


class OpenAccountForm(forms.Form):
    account_type = forms.ChoiceField(choices=[("SAVING", "Savings Account"), ("CHECKING", "Checking Account")])


class LandingView(View):
    def get(self, request, *args, **kwargs):
        pass

    def post(self, request):
        pass

