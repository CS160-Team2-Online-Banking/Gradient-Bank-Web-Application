from bankapi.models import *
from accounts.models import *
from django.conf import settings
from django.core import serializers
from django.db.models import Sum, Count, Avg
from django.db.models.functions import *
from bankapi.transfer.exchange_processor import ExchangeProcessor
import json


truncFuncs = {"YEAR": TruncYear,
              "MONTH": TruncMonth,
              "WEEK": TruncWeek}


def get_customer_count(auth_token):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    count = Customer.objects.all().count()

    return {"success": True, "data": {"users_count": count}}


def get_exchange_count(auth_token):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    count = ExchangeHistory.objects.all().count()

    return {"success": True, "data": {"exchanges_count": count}}


def get_failed_transactions(auth_token):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    bad_exchanges = ExchangeHistory.objects.filter(status=ExchangeHistory.ExchangeHistoryStatus.FAILED)
    serialized_records = json.loads(serializers.serialize("json", bad_exchanges))
    serialized_records = list(map(lambda x: x["fields"], serialized_records))

    return {"success": True, "data": {"exchanges": serialized_records}}


def get_total_savings(auth_token):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    total_savings = Accounts.objects.aggregate(Sum('balance'))

    return {"success": True, "data": {"total_savings": total_savings}}


def get_customers(auth_token):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    customers = Customer.objects.all().order_by('customer_name')
    serialized_records = json.loads(serializers.serialize("json", customers))
    for record in serialized_records: record["fields"]["pk"] = record["pk"]
    serialized_records = list(map(lambda x: x["fields"], serialized_records))

    for user in serialized_records:  # get customers and their account information
        if not user.get("pk", False):
            print("get_customers isn't attaching the primary key")
        owner_id = user["pk"]
        customer_accounts = Accounts.objects.filter(owner_id=owner_id)

        account_records = json.loads(serializers.serialize("json", customer_accounts))
        for record in account_records: record["fields"]["pk"] = record["pk"]
        account_records = list(map(lambda x: x["fields"], account_records))

        user["accounts"] = account_records

    # add each customer's accounts
    return {"success": True, "data": {"users": serialized_records}}


def get_account_transactions(auth_token, account_no):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    exchange_history = ExchangeProcessor.get_exchange_history(account_no=account_no, auth_token=auth_token)

    return {"success": True, "data": {"account_exchanges": exchange_history}}


### ADVANCED QUERIES ###


def get_customer_growth_over_time(auth_token, start_date, end_date, time_delta="MONTH"):
    pass


def get_exchanges_over_time(auth_token, start_date, end_date, time_delta="MONTH"):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    truncFunc = truncFuncs.get(time_delta, TruncMonth)

    # select exchanges, group by the month of the year, count the number of exchanges per month
    exchanges_per_time = ExchangeHistory\
        .objects\
        .filter(posted__range=[start_date, end_date])\
        .annotate(posted_time=truncFunc('posted'))\
        .values('posted_time')\
        .annotate(count=Count('pk'))

    serialized_records = json.loads(serializers.serialize("json", exchanges_per_time))
    #serialized_records = list(map(lambda x: x["fields"], serialized_records))

    return {"success":  True, "data": serialized_records}  # i'm not quite sure how to serialize this


def get_spending(auth_token, customer_id, time_delta="MONTH"):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    truncFunc = truncFuncs.get(time_delta, TruncMonth)

    customer = Customer.objects.filter(pk=customer_id).first()

    if customer is None:
        return {"success": False, "msg": "Customer doesn't exist"}

    accounts = Accounts.objects.filter(owner_id=customer.pk)

    if not len(accounts):
        return {"success": False, "msg": "Customer has no accounts"}

    account_nos = list(map(lambda x: x.account_number, accounts))

    #  calculate a users average spending on a monthly basis
    spending_per_time = ExchangeHistory\
        .objects\
        .filter(from_routing_no=settings.BANK_ROUTING_NUMBER,
                from_account_no__in=account_nos,
                status=ExchangeHistory.ExchangeHistoryStatus.FINISHED)\
        .annotate(posted_time=truncFunc('posted'))\
        .annotate(total_spending=Sum("amount"))

    serialized_records = json.loads(serializers.serialize("json", spending_per_time))
    #serialized_records = list(map(lambda x: x["fields"], serialized_records))

    return {"success":  True, "data": serialized_records}  # i'm not quite sure how to serialize this


def get_income(auth_token, customer_id, time_delta="MONTH"):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    truncFunc = truncFuncs.get(time_delta, TruncMonth)

    customer = Customer.objects.filter(pk=customer_id).first()

    if customer is None:
        return {"success": False, "msg": "Customer doesn't exist"}

    accounts = Accounts.objects.filter(owner_id=customer.pk)

    if not len(accounts):
        return {"success": False, "msg": "Customer has no accounts"}

    account_nos = list(map(lambda x: x.account_number, accounts))

    spending_per_time = ExchangeHistory\
        .objects\
        .filter(from_routing_no=settings.BANK_ROUTING_NUMBER,
                from_account_no__in=account_nos,
                status=ExchangeHistory.ExchangeHistoryStatus.FINISHED)\
        .annotate(posted_time=truncFunc('posted'))\
        .annotate(total_spending=Sum("amount"))

    serialized_records = json.loads(serializers.serialize("json", spending_per_time))
    #serialized_records = list(map(lambda x: x["fields"], serialized_records))

    return {"success":  True, "data": serialized_records}  # i'm not quite sure how to serialize this