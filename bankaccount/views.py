from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from django import forms


class OpenAccountForm(forms.Form):
    account_type = forms.ChoiceField(choices=[("SAVING", "Savings Account"), ("CHECKING", "Checking Account")])



class OpenAccountView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'base_form.html',
                          {"form": OpenAccountForm(), "form_title": "Open Account",
                           "action": "/bankaccount/"})
        else:
            return render(request, 'feature_access_message.html', {"title": "Open Bank Account",
                                                                   "message": "Please login before attempting to open a bank account"})

    def post(self, request):
        form = OpenAccountForm(request.POST)
        if form.is_valid():
            api_post_account(request.user, form.cleaned_data["account_type"])
        else:
            print("Invalid form data")
        return redirect(to="/landing/")


OpenAccount = OpenAccountView.as_view()
