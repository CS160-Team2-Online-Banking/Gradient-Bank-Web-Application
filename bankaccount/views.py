from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from django import forms
from check_image_management import get_check_image

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
            api_post_account(request, form.cleaned_data["account_type"])
        else:
            print("Invalid form data")
        return redirect(to="/landing/")


class ViewAccountDetails(View):
    def get(self, request, account_no):
        if request.user.is_authenticated:
            result = api_get_account_details(request, account_no)
            if not result or not len(result):
                return render(request, 'feature_access_message.html', {"title": "Account Details",
                                                                       "message": "Account could not be found"})
            for exchange in result[0]["exchange_history"]:
                if exchange["type"] == 'DEPOSIT':
                    img = get_check_image(request.user, exchange["from_account_no"], exchange["pk"])
                    if img:
                        exchange["image"] = img.decode("utf-8")
            return render(request, 'bankaccounts/details.html', {"account": result[0]})
        else:
            return render(request, 'feature_access_message.html', {"title": "Account Details",
                                                                   "message": "Please Login before viewing this account"})


OpenAccount = OpenAccountView.as_view()
AccountDetails = ViewAccountDetails.as_view()
