from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import forms
from api_requests.api_requests import *
from django.conf import settings
from django.contrib import messages
from django.core.validators import *
from check_image_management import save_check_image
from accounts.auth_helpers import *
from django.utils.decorators import method_decorator
from datetime import date
from decimal import *

FREQUENCY_CHOICES = [
    ("DAILY", "Daily"),
    ("WEEKLY", "Weekly"),
    ("MONTHLY", "Monthly"),
    ("YEARLY", "Yearly")
]


class AutopaymentForm(forms.Form):
    from_account = forms.ChoiceField(
        choices=[])
    amount = forms.DecimalField(label="Amount", decimal_places=2, validators=[MinValueValidator(0)])
    #to_routing_no = forms.IntegerField(label="To Routing Number", validators=[MaxValueValidator(999_999_999), MinValueValidator(0)])
    to_routing_no = forms.CharField(max_length=9, min_length=9, label="To Routing Number", validators=[RegexValidator(regex=r'^[0-9]*$')])
    #to_account_no = forms.IntegerField(label="To Account Number", validators=[MaxValueValidator(9999_9999_9999), MinValueValidator(0)])
    to_account_no = forms.CharField(max_length=12, min_length=10, label="To Account Number", validators=[RegexValidator(regex=r'^[0-9]*$')])
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES)
    start_date = forms.DateField(widget=forms.DateInput(
        format='%m-%d-%Y', attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(
        format='%m-%d-%Y', attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        from_accounts = kwargs.pop('from_accounts', [])
        super(AutopaymentForm, self).__init__(*args, **kwargs)
        from_accounts = list(map(lambda x: (x["account_number"],
                                            "{account_type}{account_number}"
                                            .format(account_type=x["account_type"]["account_type_name"],
                                                    account_number=x["account_number"])), from_accounts))
        if from_accounts:
            self.fields['from_account'].choices = from_accounts

    def is_valid(self):
        if super().is_valid():
            start_date = self.cleaned_data["start_date"]
            end_date = self.clean()["end_date"]
            if date.today() < start_date < end_date:
                return True
            else:
                if date.today() > start_date:
                    self.add_error('start_date', 'Invalid start date, please ensure the start date is some time in the future')
                if start_date > end_date:
                    self.add_error('end_date', 'Invalid end date, please ensure teh end date is after the start date')
            return False



class DepositForm(forms.Form):
    to_account = forms.ChoiceField(
        choices=[])
    #from_routing_no = forms.IntegerField(label="Check Routing Number", validators=[MaxValueValidator(999_999_999), MinValueValidator(0)])
    from_routing_no = forms.CharField(max_length=9, min_length=9, label="Check Routing Number",
                                    validators=[RegexValidator(regex=r'^[0-9]*$')])
    #from_account_no = forms.IntegerField(label="Check Account Number", validators=[MaxValueValidator(9999_9999_9999), MinValueValidator(0)])
    from_account_no = forms.CharField(max_length=12, min_length=10, label="Check Account Number",
                                    validators=[RegexValidator(regex=r'^[0-9]*$')])
    amount = forms.DecimalField(label="Amount", decimal_places=2, validators=[MinValueValidator(0)])
    image = forms.ImageField()

    def __init__(self, *args, **kwargs):
        from_accounts = kwargs.pop('from_accounts', [])
        super(DepositForm, self).__init__(*args, **kwargs)
        from_accounts = list(map(lambda x: (x["account_number"],
                                            "{account_type}{account_number}"
                                            .format(account_type=x["account_type"]["account_type_name"],
                                                    account_number=x["account_number"])), from_accounts))
        if from_accounts:
            self.fields['to_account'].choices = from_accounts


class PersonalTransferForm(forms.Form):
    from_account = forms.ChoiceField(
        choices=[])
    to_account_no = forms.ChoiceField(
        choices=[])
    amount = forms.DecimalField(label="Amount", decimal_places=2, validators=[MinValueValidator(0)])

    def __init__(self, *args, **kwargs):
        from_accounts = kwargs.pop('from_accounts', [])
        super(PersonalTransferForm, self).__init__(*args, **kwargs)
        from_accounts = list(map(lambda x: (x["account_number"],
                                            "{account_type}{account_number}"
                                            .format(account_type=x["account_type"]["account_type_name"],
                                                    account_number=x["account_number"])), from_accounts))
        if from_accounts:
            self.fields['from_account'].choices = from_accounts
            self.fields['to_account_no'].choices = from_accounts


class TransferForm(forms.Form):
    from_account = forms.ChoiceField(
        choices=[])
    #to_routing_no = forms.IntegerField(label="To Routing Number", validators=[MaxValueValidator(999_999_999), MinValueValidator(0)])
    to_routing_no = forms.CharField(max_length=9, min_length=9, label="To Routing Number",
                                    validators=[RegexValidator(regex=r'^[0-9]*$')])
    #to_account_no = forms.IntegerField(label="To Account Number", validators=[MaxValueValidator(9999_9999_9999), MinValueValidator(0)])
    to_account_no = forms.CharField(max_length=12, min_length=10, label="To Account Number",
                                    validators=[RegexValidator(regex=r'^[0-9]*$')])
    amount = forms.DecimalField(label="Amount", decimal_places=2, validators=[MinValueValidator(0)])

    def __init__(self, *args, **kwargs):
        from_accounts = kwargs.pop('from_accounts', [])
        super(TransferForm, self).__init__(*args, **kwargs)
        from_accounts = list(map(lambda x: (x["account_number"],
                                            "{account_type}{account_number}"
                                            .format(account_type=x["account_type"]["account_type_name"],
                                                    account_number=x["account_number"])), from_accounts))
        if from_accounts:
            self.fields['from_account'].choices = from_accounts


@method_decorator(customer_login_required, name='dispatch')
class Transaction(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request)
            if not from_accounts:
                from_accounts = []
        else:
            from_accounts = None

        if from_accounts:
            return render(request, 'base_form.html',
                          {"form": AutopaymentForm(from_accounts=from_accounts), "form_title": "Setup Autopayment",
                           "action": "/transaction/autopayments"})
        else:
            return render(request, 'feature_access_message.html', {"title": "Setup Autopayment",
                                                                   "message": "You cannot setup autopayments unless you have accounts"})

    def post(self, request):
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request)
            if not from_accounts:
                from_accounts = []
        form = AutopaymentForm(request.POST, from_accounts=from_accounts)
        if form.is_valid():
            data = form.cleaned_data
            result = api_setup_autopayment(request, data["to_account_no"], data["to_routing_no"],
                                           data["from_account"], str(
                                               data["amount"]), data["start_date"].isoformat(),
                                           data["end_date"].isoformat(), data["frequency"])
            if not result:
                # add fail message
                messages.error(request, 'Failed to schedule auto payment: make sure there is enough money in the account to make a transfer')
            else:
                messages.success(
                    request, 'Your auto payment has been scheduled.')
                return redirect(to="/")
        else:
            print("Invalid form data")
        return render(request, 'base_form.html', {"form": form,
                                                  "form_title": "Autopayment Configured",
                                                  "action": "/transaction/autopayments"})


@method_decorator(customer_login_required, name='dispatch')
class TransferView(View):
    def get(self, request, type=None):
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request)
            if not from_accounts:
                return render(request, 'feature_access_message.html', {"title": "Setup Transfer",
                                                                       "message": "You cannot transfer money without bank accounts"})
            form = PersonalTransferForm(from_accounts=from_accounts)
            if type == "/external":
                form = TransferForm(from_accounts=from_accounts)
            return render(request, 'base_form.html', {"form": form, "form_title": "Transfer Money",
                                                      "action": "/transaction/transfers{type}".format(type=type)})
        else:
            return render(request, 'feature_access_message.html', {"title": "Account Details",
                                                                   "message": "Please Login before transferring money"})

    def post(self, request, type=None):
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request)

            if type == "/external":
                form = TransferForm(request.POST, from_accounts=from_accounts)
            else:
                form = PersonalTransferForm(
                    request.POST, from_accounts=from_accounts)

            if form.is_valid():
                data = form.cleaned_data
                to_routing_no = data.get(
                    "to_routing_no", settings.BANK_ROUTING_NUMBER)

                if to_routing_no == settings.BANK_ROUTING_NUMBER and data["from_account"] == data["to_account_no"]:
                    messages.error(request, "You cannot transfer between the same account")
                    return render(request, 'base_form.html', {"form": form, "form_title": "Transfer Money",
                                  "action": "/transaction/transfers{type}".format(type=type)})

                result = api_post_transfer(request, data["to_account_no"], to_routing_no,
                                           data["from_account"], str(data["amount"]))
                if not result:
                    print("Request Failed")

                return redirect(reverse('bankaccount:accountdetails', kwargs={"account_no": data["from_account"]}))
            else:
                return render(request, 'base_form.html', {"form": form, "form_title": "Transfer Money",
                                                          "action": "/transaction/transfers{type}".format(type=type)})
        else:
            return render(request, 'feature_access_message.html', {"title": "Account Details",
                                                                   "message": "Please Login before transferring money"})


@method_decorator(customer_login_required, name='dispatch')
class DepositView(View):
    def get(self, request):
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request)
            if not from_accounts:
                return render(request, 'feature_access_message.html', {"title": "Setup Deposit",
                                                                       "message": "You cannot deposit money without accounts"})
            form = DepositForm(from_accounts=from_accounts)
            if not from_accounts:
                from_accounts = []
        else:
            return render(request, 'feature_access_message.html', {"title": "Account Details",
                                                                   "message": "Please Login before transferring money"})

        if from_accounts:
            return render(request, 'base_form.html',
                          {"form": DepositForm(from_accounts=from_accounts), "form_title": "Check Deposit",
                           "action": "/transaction/deposit"})
        else:
            return render(request, 'feature_access_message.html', {"title": "Check Deposit",
                                                                   "message": "You cannot deposit unless you have accounts"})

    def post(self, request):
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request)
            if not from_accounts:
                from_accounts = []
        else:
            return render(request, 'feature_access_message.html', {"title": "Account Details",
                                                                   "message": "Please Login before transferring money"})
        form = DepositForm(request.POST, request.FILES,
                           from_accounts=from_accounts)

        if form.is_valid():
            data = form.cleaned_data
            to_routing_no = data.get(
                "to_routing_no", settings.BANK_ROUTING_NUMBER)
            result = api_post_check_deposit(request, data["to_account"], data["from_account_no"],
                                            data["from_routing_no"], str(data["amount"]))
            if result:
                file = request.FILES['image']
                exchange_id = result["transfer_id"]
                save_check_image(request.user, data["to_account"], exchange_id, file)
            else:
                print("Request Failed")

            # render(request, 'base_form.html', {"form": form, "form_title": "Check Deposit","action": "/transaction/deposit".format(type=type)})
            return redirect(reverse('bankaccount:accountdetails', kwargs={"account_no": data["to_account"]}))
        return render(request, 'base_form.html',
                      {"form": form, "form_title": "Check Deposit",
                       "action": "/transaction/deposit"})

transaction = Transaction.as_view()
transfer = TransferView.as_view()
deposit = DepositView.as_view()
