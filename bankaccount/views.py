from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from django import forms
from check_image_management import get_check_image
from django.contrib import messages


class OpenAccountForm(forms.Form):
    account_type = forms.ChoiceField(choices=[("SAVING", "Savings Account"), ("CHECKING", "Checking Account")])


class OpenAccountView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'base_form.html',
                          {"form": OpenAccountForm(), "form_title": "Open Account",
                           "action": "/bankaccount/"})
        else:
            messages.info(request, "Please login before attempting to open a bank account")
            return redirect(to="/landing/")

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
                messages.info(request, "Account could not be found")
                return redirect(to="/landing/")

            for exchange in result[0]["exchange_history"]:
                if "type" in exchange and exchange["type"] == 'DEPOSIT':
                    img = get_check_image(request.user, exchange["from_account_no"], exchange["pk"])
                    if img:
                        exchange["image"] = img.decode("utf-8")

                if "amount" in exchange:
                    if exchange["amount"][0] == '-':
                        exchange["amount"] = "-$"+exchange["amount"][1:]
                    else:
                        exchange["amount"] = "$"+exchange["amount"]

            return render(request, 'bankaccounts/details.html', {"account": result[0]})
        else:
            messages.info(request, "Please Login before viewing this account")
            return redirect(to="/landing/")


    def post(self, request, account_no):
        if request.user.is_authenticated:
            if (request.POST.get("type", "") == "Close Account"):
                result = api_close_account(request, account_no)
                if not result:
                    messages.info(request, "Your request to close the bank "
                                           "account was denied.Please make sure "
                                           "you transfer any money out of the"
                                           " account before attempting to close"
                                           " it.")
                    return redirect(to="/bankaccount/details/{account_no}".format(account_no=account_no))
                messages.info(request, "You have successfully closed your account")
                return redirect(to="/landing/")
        else:
            return render(request, 'feature_access_message.html', {"title": "Account View",
                                                                       "message": "Please Login before closing this account"})


OpenAccount = OpenAccountView.as_view()
AccountDetails = ViewAccountDetails.as_view()
