from bankapi.models import *
from accounts.models import *
from django.conf import settings
from django.core import serializers
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import *
import ipaddress
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

    return {"success": True, "data": {"total_savings": total_savings['balance__sum']}}


def get_customers(auth_token, verbose=False, page_size=10, page_number=0, order_by='customer_name', **search_criteria):
    manager_id = auth_token.get("manager_id", None)
    page_size = int(page_size)
    page_number = int(page_number)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    if len(search_criteria):
        customers = Customer.objects.filter(**search_criteria).order_by(order_by)
    else:
        customers = Customer.objects.all().order_by(order_by)
    paginator = Paginator(customers, per_page=page_size)
    page_count = len(paginator.page_range)
    page = paginator.get_page(page_count-1-page_number)

    serialized_records = json.loads(serializers.serialize("json", page.object_list))
    #serialized_records.reverse()
    #serialized_records = page.object_list
    for record in serialized_records: record["fields"]["pk"] = record["pk"]
    serialized_records = list(map(lambda x: x["fields"], serialized_records))

    for user in serialized_records:  # get customers and their account information
        owner_id = user["pk"]
        if verbose:
            if not user.get("pk", False):
                print("get_customers isn't attaching the primary key")

            customer_accounts = Accounts.objects.filter(owner_id=owner_id)

            account_records = json.loads(serializers.serialize("json", customer_accounts))
            for record in account_records: record["fields"]["pk"] = record["pk"]
            account_records = list(map(lambda x: x["fields"], account_records))

            user["accounts"] = account_records
        else:
            user["accounts"] = len(Accounts.objects.filter(owner_id=owner_id))

    # add each customer's accounts
    return {"success": True, "data": {"users": serialized_records, "page_count": page_count}}


def get_account_transactions(auth_token, account_no):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success":  False, "msg": "Access Denied"}

    exchange_history = ExchangeProcessor.get_exchange_history(account_no=account_no, auth_token=auth_token)

    return exchange_history


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

    #serialized_records = json.loads(serializers.serialize("json", exchanges_per_time))
    #serialized_records = list(map(lambda x: x["fields"], serialized_records))

    return {"success":  True, "data": list(exchanges_per_time)}  # i'm not quite sure how to serialize this


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
        .filter(~Q(to_account_no__in=account_nos),
                Q(status=ExchangeHistory.ExchangeHistoryStatus.FINISHED)|
                Q(status=ExchangeHistory.ExchangeHistoryStatus.POSTED),
                from_routing_no=settings.BANK_ROUTING_NUMBER,
                from_account_no__in=account_nos) \
        .annotate(posted_delta_time=truncFunc('posted')) \
        .values('posted_delta_time') \
        .annotate(total_spending=Sum("amount")) \
        .values('posted_delta_time', 'total_spending')

    #serialized_records = json.loads(serializers.serialize("json", spending_per_time))
    #serialized_records = list(map(lambda x: x["fields"], serialized_records))

    return {"success":  True, "data": list(spending_per_time)}  # i'm not quite sure how to serialize this


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

    income_per_time = ExchangeHistory\
        .objects\
        .filter(~Q(from_account_no__in=account_nos),
                Q(status=ExchangeHistory.ExchangeHistoryStatus.FINISHED)|
                Q(status=ExchangeHistory.ExchangeHistoryStatus.POSTED),
                to_routing_no=settings.BANK_ROUTING_NUMBER,
                to_account_no__in=account_nos)\
        .annotate(posted_delta_time=truncFunc('posted')) \
        .values('posted_delta_time') \
        .annotate(total_income=Sum("amount")) \
        .values('posted_delta_time', 'total_income')

    #serialized_records = json.loads(serializers.serialize("json", spending_per_time))
    #serialized_records = list(map(lambda x: x["fields"], serialized_records))

    return {"success":  True, "data": list(income_per_time)}  # i'm not quite sure how to serialize this


def get_customer_activity(auth_token, customer_id):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success": False, "msg": "Access Denied"}

    activity_log = EventLog.objects.filter(intiator_user_id=customer_id)
    pk_ip_info = {}
    for record in activity_log:
         pk_ip_info[record.pk] = (None if not record.ip4_address else ipaddress.ip_address(record.ip4_address).compressed,
         None if not record.ip6_address else ipaddress.ip_address(record.ip6_address).compressed)

    serialized_records = json.loads(serializers.serialize("json", activity_log))
    for record in serialized_records: record["fields"]["pk"] = record["pk"]
    serialized_records = list(map(lambda x: x["fields"], serialized_records))
    for record in serialized_records:
        record["event_type"] = EventTypes.EVENT_ARR[int(record["event_type"])][1]
        record["ip4_address"] = pk_ip_info[record["pk"]][0]
        record["ip6_address"] = pk_ip_info[record["pk"]][1]
    # add each customer's accounts
    return {"success": True, "data": serialized_records}


def get_customer_account_info(auth_token, customer_id):
    manager_id = auth_token.get("manager_id", None)

    if manager_id is None:
        return {"success": False, "msg": "Access Denied"}

    customer_accounts = Accounts.objects.filter(owner_id=customer_id)
    account_records = json.loads(serializers.serialize("json", customer_accounts))
    for record in account_records: record["fields"]["pk"] = record["pk"]
    account_records = list(map(lambda x: x["fields"], account_records))

    for i, entry in enumerate(account_records):
        account_type_id = int(entry["account_type"])
        account_type = AccountTypes.objects.get(pk=account_type_id)
        entry["account_type"] = {"account_type_id": account_type.pk,
                                 "account_type_name": account_type.account_type_name}

    return {"success": True, "data": account_records}


REPORT_DISPATCHER = {
    "get_income": get_income,
    "get_spending": get_spending,
    "get_exchanges_over_time": get_exchanges_over_time,
    "get_account_transactions": get_account_transactions,
    "get_customers": get_customers,
    "get_total_savings": get_total_savings,
    "get_failed_transactions": get_failed_transactions,
    "get_exchange_count": get_exchange_count,
    "get_customer_count": get_customer_count,
    "get_customer_activity": get_customer_activity,
    "get_customer_account_info": get_customer_account_info
}


def default_dipatcher():
    return {"success": False, "msg": "The report type you requested doesn't exist"}


def dispatch_report(report_name):
    return REPORT_DISPATCHER.get(report_name, default_dipatcher)