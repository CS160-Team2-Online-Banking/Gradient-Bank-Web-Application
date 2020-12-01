from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import *
from django.core.validators import *
from django.db import transaction
from .state_choices import STATE_CHOICES
from django.core.validators import *
from .models import CustomerUser, BankManagerUser
from bankapi.models import Customer

phone_regex = r'(?P<ier>1)?(?:-| )?(?P<acd>[(]\d{3}[)]|\d{3})(?:-| )?(?P<lnn>\d{3})(?:-| )?(?P<pnn>\d{4})'


def get_phone_number(data):
    m = re.match(phone_regex, data)
    if m and m.groups():
        m_dict = m.groupdict()
        extension = m_dict['ier'] if m_dict['ier'] is not None else ''
        parsable_str = '{ier}{acd}{lnn}{pnn}'.format(ier=extension,
                                                     acd=m_dict['acd'].replace('(','').replace(')',''),
                                                     lnn=m_dict['lnn'],
                                                     pnn=m_dict['pnn'])
        return int(parsable_str)
    raise ValueError()


def to_phone_number(number):
    str_num = str(number).zfill(11)
    if str_num[0]=='0':
        str_num = str_num[1:]
        return '({acd}) {lnn}-{pnn}'.format(acd=str_num[:3], lnn=str_num[3:6], pnn=str_num[6:10])
    return '{ier} ({acd}) {lnn}-{pnn}'.format(ier=str_num[0], acd=str_num[1:4], lnn=str_num[4:7], pnn=str_num[7:11])


class CustomerUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label="First Name")
    middle_initial = forms.CharField(max_length=1, label="Middle Initial (Optional)", required=False)
    last_name = forms.CharField(max_length=50, label="Last Name")
    address = forms.CharField(max_length=50, label="Mailing Address")
    #ssn = forms.IntegerField(label="Social Security Number", validators=[MaxValueValidator(999_99_9999), MinValueValidator(0)])
    ssn = forms.CharField(label="Social Security Number", validators=[RegexValidator(regex=r'^[0-9]*$'), MinLengthValidator(9)])
    phone = forms.CharField(label="Phone Number", validators=[RegexValidator(regex=phone_regex)])
    username = forms.CharField(max_length=50, label="Username")
    zip = forms.CharField(max_length=5, label="Zip Code", validators=[RegexValidator(regex=r'^[0-9]*$'), MinLengthValidator(5)])
    city = forms.CharField(max_length=45, label="City")
    state = forms.ChoiceField(choices=STATE_CHOICES, label="State")
    pin = forms.CharField(label="PIN", max_length=4, validators=[RegexValidator(regex=r'^[0-9]*$'), MinLengthValidator(4)])
    email = forms.EmailField()

    def register_user(self):
        cleaned_data = self.cleaned_data
        data_dict = self.cleaned_data
        data_dict["phone"] = get_phone_number(data_dict["phone"])
        if cleaned_data['password1'] == cleaned_data['password2']:
            cleaned_data['password'] = cleaned_data['password1']
        else:
            return None
        print("User Registration")
        print(data_dict)
        user = CustomerUser.objects.create_user(**data_dict)
        return user

    class Meta(UserCreationForm):
        model = CustomerUser
        fields = ('first_name', 'middle_initial', 'last_name', 'username', 'email', 'address', "zip", "city", "state", 'ssn', "pin", 'phone')


class CustomerUserChangeForm(UserChangeForm):
    first_name = forms.CharField(max_length=50, label="First Name")
    middle_initial = forms.CharField(max_length=1, label="Middle Initial (Optional)", required=False)
    last_name = forms.CharField(max_length=50, label="Last Name")
    address = forms.CharField(max_length=50, label="Mailing Address")
    #ssn = forms.IntegerField(label="Social Security Number", validators=[MaxValueValidator(999_99_9999), MinValueValidator(0)])
    ssn = forms.CharField(label="Social Security Number",
                          validators=[RegexValidator(regex=r'^[0-9]*$'), MinLengthValidator(9)])
    phone = forms.CharField(label="Phone Number", validators=[RegexValidator(regex=phone_regex)])
    username = forms.CharField(max_length=50, label="Username")
    zip = forms.CharField(max_length=5, label="Zip Code", validators=[RegexValidator(regex=r'^[0-9]*$'), MinLengthValidator(5)])
    city = forms.CharField(max_length=45, label="City")
    state = forms.ChoiceField(choices=STATE_CHOICES, label="State")
    pin = forms.CharField(label="PIN", max_length=4, validators=[RegexValidator(regex=r'^[0-9]*$'), MinLengthValidator(4)])
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(CustomerUserChangeForm, self).__init__(*args, **kwargs)  # call parent's constructor
        if self.instance:
            user = self.instance
            customer_data = Customer.objects.filter(pk=user.pk).first()
            if customer_data:
                namebits = customer_data.customer_name.split(" ")
                if len(namebits)==3:
                    self.initial["first_name"] = namebits[0]
                    self.initial["middle_initial"] = namebits[1]
                    self.initial["last_name"] = namebits[2]
                elif len(namebits)==2:
                    self.initial["first_name"] = namebits[0]
                    self.initial["last_name"] = namebits[1]
                self.initial["address"]=customer_data.customer_address
                self.initial["ssn"]=customer_data.customer_ssn
                self.initial["phone"]=to_phone_number(customer_data.customer_phone)
                self.initial["zip"]=customer_data.customer_zip
                self.initial["city"]=customer_data.customer_city
                self.initial["state"]=customer_data.customer_state
                self.initial["pin"]=customer_data.customer_pin

    def save(self, commit=True):
        m = super(CustomerUserChangeForm, self).save(commit=False)
        data_dict = self.cleaned_data
        data_dict["phone"] = get_phone_number(data_dict["phone"])
        bank_cust = CustomerUser.objects.update_user_info(m, commit=False, **data_dict)
        # add change password here
        #
        if commit:
            m.save()
            bank_cust.save()

    class Meta(UserCreationForm):
        model = CustomerUser
        fields = ('first_name', 'middle_initial', 'last_name', 'username', 'email', 'address', "zip", "city", "state", 'ssn', "pin", 'phone')

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

