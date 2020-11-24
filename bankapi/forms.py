from django.contrib.auth.forms import *
from django.core.validators import *


class ATMForm(forms.Form):
    bank_username = forms.CharField(label="Username", max_length=255)
    account_no = forms.IntegerField(label="Account Number", validators=[MaxValueValidator(9999_9999_9999), MinValueValidator(0)])
    bank_pin = forms.CharField(label="PIN", max_length=4, validators=[RegexValidator(regex=r'^[0-9]*$')], widget=forms.PasswordInput())
    amount = forms.DecimalField(label="Amount", decimal_places=2, validators=[MinValueValidator(0)])

