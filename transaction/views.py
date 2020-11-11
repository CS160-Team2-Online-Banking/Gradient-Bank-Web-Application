from django.shortcuts import render
from django.views import View
from django import forms
from api_requests.api_requests import *


FREQUENCY_CHOICES = [
    ("DAILY", "Daily"),
    ("WEEKLY", "Weekly"),
    ("MONTHLY", "Monthly"),
    ("YEARLY", "Yearly")
]


class AutopaymentForm(forms.Form):
    from_account = forms.ChoiceField(choices=[("None", "You have no accounts")])
    amount = forms.DecimalField(label="Amount", decimal_places=2)
    to_routing_no = forms.IntegerField(label="To Routing Number")
    to_account_no = forms.IntegerField(label="To Account Number")
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES)
    start_date = forms.DateField(widget=forms.DateInput(format='%m-%d-%Y', attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(format='%m-%d-%Y', attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        from_accounts = kwargs.pop('from_accounts', [])
        super(AutopaymentForm, self).__init__(*args, **kwargs)
        if from_accounts:
            self.fields['from_account'].choices = from_accounts


class TransferForm(forms.Form):
    from_account = forms.ChoiceField(choices=[("None", "You have no accounts")])
    amount = forms.DecimalField(label="Amount", decimal_places=2)
    to_routing_no = forms.IntegerField(label="To Routing Number")
    to_account_no = forms.IntegerField(label="To Account Number")

    def __init__(self, *args, **kwargs):
        from_accounts = kwargs.pop('from_accounts', [])
        super(AutopaymentForm, self).__init__(*args, **kwargs)
        if from_accounts:
            self.fields['from_account'].choices = from_accounts


class Transaction(View):
    def get(self, request, *args, **kwargs):
        result = []
        if request.user.is_authenticated:
            from_accounts = api_get_accounts(request.user)
            if not from_accounts:
                from_accounts = []
        if from_accounts:
            return render(request, 'base_form.html',
                          {"form": AutopaymentForm(from_accounts=result), "form_title": "Setup Autopayment",
                           "action": "/transaction/"})
        else:
            return render(request, 'feature_access_message.html', {"title": "Setup Autopayment",
                                                                   "message": "You cannot setup autopayments unless you have accounts"})

    def post(self, request):
        form = AutopaymentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = api_setup_autopayment(request.user, data["to_account_no"], data["to_routing_no"],
                                           data["from_account"], str(data["amount"]), data["start_date"].isoformat(),
                                           data["end_date"].isoformat(), data["frequency"])
            if not result:
                print("Request Failed")
        else:
            print("Invalid form data")
        return render(request, 'base_form.html', {"form": form, "form_title": "Autopayment Configured", "action":"/transaction/"})


transaction = Transaction.as_view()
