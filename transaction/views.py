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
        from_accounts = kwargs.pop('from_accounts')
        super(AutopaymentForm, self).__init__(*args, **kwargs)
        if from_accounts:
            self.fields['from_account'].choices = from_accounts


class TransferForm(forms.Form):
    from_account = forms.ChoiceField(choices=[("None", "You have no accounts")])
    amount = forms.DecimalField(label="Amount", decimal_places=2)
    to_routing_no = forms.IntegerField(label="To Routing Number")
    to_account_no = forms.IntegerField(label="To Account Number")

    def __init__(self, *args, **kwargs):
        from_accounts = kwargs.pop('from_accounts')
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
        return render(request, 'base_form.html', {"form": AutopaymentForm(from_accounts=result), "action": "/transaction/"})

    def post(self, request):
        pass


transaction = Transaction.as_view()
