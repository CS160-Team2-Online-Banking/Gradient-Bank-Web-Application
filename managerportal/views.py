from django.shortcuts import render
from django.views import View
from api_requests.api_requests import *
from django.shortcuts import redirect
from django import forms
from accounts.models import BankManagerUser
from .requests import api_get_data
from django.http import HttpResponseForbidden
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime


class OpenAccountForm(forms.Form):
    account_type = forms.ChoiceField(choices=[("SAVING", "Savings Account"), ("CHECKING", "Checking Account")])


def get_manager(user):
    if user.is_authenticated:
        return BankManagerUser.objects.filter(pk=user.pk).first()
    return None


class CustomersSearchForm(forms.Form):
    order_by = forms.CharField(label=None, widget=forms.HiddenInput(), initial='customer_name', required=False)
    page_number = forms.IntegerField(label=None, initial=1, required=False, validators=[])
    page_count = forms.IntegerField(widget=forms.HiddenInput(), label=None, initial=1, required=False)
    customer_name = forms.CharField(label="Customer Name", required=False)
    customer_phone = forms.IntegerField(label="Phone Number", required=False)
    customer_email = forms.CharField(label="Customer Email", required=False)
    customer_ssn = forms.CharField(label="Customer SSN", required=False)
    customer_address = forms.CharField(label="Customer Address", required=False)
    customer_zip = forms.CharField(label="Customer Zip", required=False)
    customer_city = forms.CharField(label="Customer City", required=False)
    customer_state = forms.CharField(label="Customer State", required=False)
    selected_customer_id = forms.IntegerField(required=False, initial=-1, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CustomersSearchForm, self).__init__(*args, **kwargs)
        #self.fields['page_number'].validators = [MinValueValidator(1), MaxValueValidator(self.fields['page_count'].initial)]


def set_or_message(result, key, dict, mapper=lambda x: x):
    if result:
        dict[key] = mapper(result)
    else:
        dict[key] = "#ERROR"


class LandingView(View):
    @staticmethod
    def get_headline(request, manager):
        start_date = datetime.utcnow() - timedelta(days=60)
        end_date = datetime.utcnow()
        headline = {}
        set_or_message(api_get_data(request, manager, "get_customer_count", {}), "customer_count", headline,
                       lambda x: list(x.values())[0])
        set_or_message(api_get_data(request, manager, "get_exchange_count", {}), "exchange_count", headline,
                       lambda x: list(x.values())[0])
        set_or_message(api_get_data(request, manager, "get_failed_transactions", {}), "failed_exchanges", headline,
                       lambda x: list(x.values())[0])
        set_or_message(api_get_data(request, manager, "get_total_savings", {}), "total_balance", headline,
                       lambda x: list(x.values())[0])
        return headline

    @staticmethod
    def prepare_customer_report(request, manager, customer_id):
        customer_accounts = api_get_data(request, manager, "get_customer_account_info", {"customer_id":customer_id})
        if customer_accounts:
            for account in customer_accounts:
                transactions = api_get_data(request, manager, "get_account_transactions", {"account_no": account["account_number"]})
                account["exchange_history"] = transactions if transactions else []

        customer_activity = api_get_data(request, manager, "get_customer_activity", {"customer_id": customer_id})
        income_history = api_get_data(request, manager, "get_income", {"customer_id": customer_id, "time_delta": "WEEK"})
        spending_history = api_get_data(request, manager, "get_spending", {"customer_id": customer_id, "time_delta": "WEEK"})
        print(income_history)
        return {
            "customer_accounts": customer_accounts if customer_accounts else [],
            "customer_activity": customer_activity if customer_activity else [],
            "income_history": income_history if income_history else [],
            "spending_history": spending_history if spending_history else []
        }

    @staticmethod
    def prep_post_params(data):
        params = {}

        def add_contains_search(key):
            if data[key]:
                params[key+"__icontains"] = data[key]

        def add_param(key):
            if data[key]:
                params[key] = data[key]
        add_contains_search('customer_name')
        add_contains_search('customer_phone')
        add_contains_search('customer_ssn')
        add_contains_search('customer_email')
        add_contains_search('customer_address')
        add_contains_search('customer_zip')
        add_contains_search('customer_city')
        add_contains_search('customer_state')
        add_param('order_by')
        data['page_number'] = str(int(data['page_number'])-1)
        add_param('page_number')
        return params

    def get(self, request, *args, **kwargs):
        user = request.user
        manager = get_manager(user)

        if manager is None:
            return HttpResponseForbidden()

        headline = self.get_headline(request, manager)
        result = api_get_data(request, manager, "get_customers", {})
        start_form = CustomersSearchForm(initial={"page_count": result["page_count"]})
        return render(request, "managerportal/landing.html", {"manager": manager, "headline": headline,
                                                              "customers_table": result,
                                                              "form": start_form,
                                                              "cust_table_page": 0,
                                                              "cust_table_query": {},
                                                              "customer_details": {}})

    def post(self, request):
        user = request.user
        manager = get_manager(user)

        if manager is None:
            return HttpResponseForbidden()

        headline = self.get_headline(request, manager)
        form = CustomersSearchForm(request.POST)
        customer_details = {}
        if form.is_valid():
            data = form.cleaned_data
            params = self.prep_post_params(data)
            result = api_get_data(request, manager, "get_customers", params)
            if data["selected_customer_id"] > 0:
                customer_details = self.prepare_customer_report(request, manager, data["selected_customer_id"])
            if not result:
                result = api_get_data(request, manager, "get_customers", {})
        else:
            result = api_get_data(request, manager, "get_customers", {})
        return render(request, "managerportal/landing.html", {"manager": manager, "headline": headline,
                                                              "customers_table": result,
                                                              "form": form,
                                                              "cust_table_page": 0,
                                                              "cust_table_query": {},
                                                              "customer_details": customer_details})

        # if it's a new search, populate the customer table with the search results and keep the results section the same
        # if it's a detail selection, populate the details section and keep the table the same

