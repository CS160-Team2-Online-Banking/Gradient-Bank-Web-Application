from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import *
from django.core.validators import *
from django.db import transaction
from .state_choices import STATE_CHOICES

from .models import CustomerUser, BankManagerUser

class CustomerUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label="First Name")
    middle_initial = forms.CharField(max_length=1, label="Middle Initial (Optional)", required=False)
    last_name = forms.CharField(max_length=50, label="Last Name")
    address = forms.CharField(max_length=50, label="Mailing Address")
    ssn = forms.IntegerField(label="Social Security Number", )
    phone = forms.IntegerField(label="Phone Number")
    username = forms.CharField(max_length=50, label="Username")
    zip = forms.CharField(max_length=5, label="Zip Code")
    city = forms.CharField(max_length=45, label="City")
    state = forms.ChoiceField(choices=STATE_CHOICES, label="State")

    def register_user(self):
        cleaned_data = self.cleaned_data
        if cleaned_data['password1'] == cleaned_data['password2']:
            cleaned_data['password'] = cleaned_data['password1']
        else:
            return None
        print("User Registration")
        print(cleaned_data)
        user = CustomerUser.objects.create_user(**cleaned_data)
        return user

    class Meta(UserCreationForm):
        model = CustomerUser
        fields = ('first_name', 'middle_initial', 'last_name', 'username', 'email', 'address', "zip", "city", "state", 'ssn', 'phone')


class BankManagerUserCreationForm(UserCreationForm):
    def register_user(self):
        cleaned_data = self.cleaned_data
        if cleaned_data['password1'] == cleaned_data['password2']:
            cleaned_data['password'] = cleaned_data['password1']
        else:
            return None

        user = BankManagerUser.objects.create_user(**cleaned_data)
        return user

    class Meta(UserCreationForm):
        model = BankManagerUser
        fields = ('email',)

