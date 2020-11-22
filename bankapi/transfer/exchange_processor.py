from bankapi.models import *
from decimal import *
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.functions import Now
from django.core import serializers
import json

SUSPICIOUS_TRANSFER_AMOUNT_MAX = 10_000


@transaction.atomic(using="bank_data")
def flag_suspicious_exchange(exchange, event):
    exchange.status = ExchangeHistory.ExchangeHistoryStatus.FLAGGED
    exchange.save()
    if event is not None:
        event.event_type = EventTypes.SUSPICIOUS_TRANSFER[0]
        event.data_id = exchange.pk
        event.save()



def is_exchange_suspicious(exchange, create_event=None):
    if create_event is None:
        return exchange.amount > SUSPICIOUS_TRANSFER_AMOUNT_MAX

    query = Q(pk__isnull=True)
    if create_event.ip4_address is not None:
        query = query | Q(ip6_address=create_event.ip6_address)
    if create_event.ip6_address is not None:
        query = query | Q(ip4_address=create_event.ip4_address)

    events_with_same_ip = EventLog.objects.filter(Q(intiator_user_id=create_event.intiator_user_id), ~Q(pk=create_event.pk))\
                                          .filter(query)
    return (not len(events_with_same_ip)) or exchange.amount > SUSPICIOUS_TRANSFER_AMOUNT_MAX


@transaction.atomic(using="bank_data")
def external_transfer_handler(auth_token, from_account_no, to_account_no, to_routing_no, amount, event=None) -> dict:
    user_id = auth_token["user_id"]
    from_account = Accounts.objects.filter(account_number=from_account_no).first()
    if amount <= 0:
        return {"success": False, "msg": "you can only transfer non-zero positive sums of money"}
    if from_account is None:
        return {"success": False, "msg": "one of the accounts specified does not exist"}

    owner_id = from_account.owner_id
    if owner_id == user_id:
        if amount <= from_account.balance:
            ex = ExchangeHistory(to_account_no=to_account_no,
                                 from_account_no=from_account_no,
                                 to_routing_no=to_routing_no,
                                 from_routing_no=settings.BANK_ROUTING_NUMBER,
                                 amount=amount,
                                 posted=Now(),
                                 status=ExchangeHistory.ExchangeHistoryStatus.POSTED)

            if is_exchange_suspicious(ex, event):
                flag_suspicious_exchange(ex, event)
                return {"success": False, "msg": "This transfer was flagged as suspicious"}

            from_account.balance = from_account.balance - amount
            from_account.save()

            ex.save()
            ext_pool = ExternalTransferPool(internal_account=from_account,
                                            external_account_routing_no=to_routing_no,
                                            external_account_no=to_account_no,
                                            amount=amount,
                                            inbound=False,
                                            debit_transfer=False,
                                            exchange_obj=ex)
            ext_pool.save()

            return {"success": True, "data": {"transfer_id": ex.pk}}
        else:
            return {"success": False, "msg": "insufficient funds"}
        return {"success": False, "msg": "insufficient permission"}


@transaction.atomic(using="bank_data")
def internal_transfer_handler(auth_token, from_account_no, to_account_no, amount, event=None) -> dict:
    user_id = auth_token["user_id"]
    from_account = Accounts.objects.filter(account_number=from_account_no).first()
    to_account = Accounts.objects.filter(account_number=to_account_no).first()

    if amount <= 0:
        return {"success": False, "msg": "you can only transfer non-zero positive sums of money"}
    if from_account is None or to_account is None:
        return {"success": False, "msg": "one of the accounts specified does not exist"}
    if from_account == to_account:
        return {"success": False, "msg": "invalid transfer"}

    owner_id = from_account.owner_id

    if owner_id == user_id:
        if amount <= from_account.balance:
            ex = ExchangeHistory(to_account_no=to_account_no,
                                 from_account_no=from_account_no,
                                 to_routing_no=settings.BANK_ROUTING_NUMBER,
                                 from_routing_no=settings.BANK_ROUTING_NUMBER,
                                 amount=amount,
                                 posted=Now(),
                                 finished=Now(),
                                 status=ExchangeHistory.ExchangeHistoryStatus.FINISHED)

            if is_exchange_suspicious(ex, event):
                flag_suspicious_exchange(ex, event)
                return {"success": False, "msg": "This transfer was flagged as suspicious"}

            from_account.balance = from_account.balance - amount
            to_account.balance = to_account.balance + amount
            from_account.save()
            to_account.save()


            ex.save()
            return {"success": True, "data": {"transfer_id": ex.pk}}
        else:
            return {"success": False, "msg": "insufficient funds"}
    return {"success": False, "msg": "insufficient permission"}


@transaction.atomic(using="bank_data")
def deposit_handler(auth_token, from_account_no, from_routing_no, to_account_no, amount, event=None) -> dict:
    requesting_user_id = auth_token["user_id"]
    debit_authorization_key = auth_token["debit_auth_key"]

    to_account = Accounts.objects.filter(account_number=to_account_no).first()

    if amount <= 0:
        return {"success": False, "msg": "you can only deposit non-zero positive sums of money"}
    if to_account is None:
        return {"success": False, "msg": "one of the accounts specified does not exist"}

    internal = from_routing_no == settings.BANK_ROUTING_NUMBER
    if internal:
        from_account = Accounts.objects.filter(account_number=from_account_no).first()
        if from_account is None:
            return {"success": False, "msg": "one of the accounts specified does not exist"}
        if from_account.balance < amount:
            return {"success": False, "msg": "insufficient funds in checking account"}

    to_owner_id = to_account.owner_id

    if requesting_user_id == to_owner_id and debit_authorization_key == settings.DEBIT_AUTH_KEY:
        ex = ExchangeHistory(to_account_no=to_account_no,
                             from_account_no=from_account_no,
                             to_routing_no=settings.BANK_ROUTING_NUMBER,
                             from_routing_no=from_routing_no,
                             amount=amount,
                             posted=Now(),
                             type=ExchangeHistory.ExchangeTypes.DEPOSIT,
                             status=ExchangeHistory.ExchangeHistoryStatus.POSTED)
        ex.save()
        to_account.balance = to_account.balance + amount
        to_account.save()

        if is_exchange_suspicious(ex, event):
            flag_suspicious_exchange(ex, event)
            return {"success": False, "msg": "This transfer was flagged as suspicious"}

        if internal:
            from_account.balance = from_account.balance - amount
            from_account.save()
        else:
            ext_pool = ExternalTransferPool(internal_account=to_account,
                                            external_account_routing_no=from_routing_no,
                                            external_account_no=from_account_no,
                                            amount=amount,
                                            inbound=True,
                                            debit_transfer=True,
                                            exchange_obj=ex)
            ext_pool.save()
        return {"success": True, "data": {"transfer_id": ex.pk}}
    return {"success": False, "msg": "insufficient permission"}

class ExchangeProcessor:
    @staticmethod
    def start_exchange(exchange_data, auth_token, event=None) -> dict:
        # the first step is to determine how to route the money
        # if it's some kind of external transfer, we need to move the money to or from a pool
        # if it's an internal transfer, we just need to move the money over (we can do this right here and be done
        to_account_no = exchange_data["to_account_no"]
        to_routing_no = exchange_data["to_routing_no"]
        from_account_no = exchange_data["from_account_no"]
        from_routing_no = exchange_data["from_routing_no"]
        amount = exchange_data["amount"]

        if from_routing_no == settings.BANK_ROUTING_NUMBER:
            if to_routing_no == settings.BANK_ROUTING_NUMBER:  # If both accounts are under our bank
                if "debit_auth_key" in auth_token:
                    result = deposit_handler(auth_token, from_account_no, from_routing_no, to_account_no, amount, event)
                else:
                    result = internal_transfer_handler(auth_token, from_account_no, to_account_no, amount, event)
            else:  # If the from account belongs to us but not the to
                result = external_transfer_handler(auth_token, from_account_no, to_account_no, to_routing_no, amount, event)
        else:
            if to_routing_no == settings.BANK_ROUTING_NUMBER:
                result = deposit_handler(auth_token, from_account_no, from_routing_no, to_account_no, amount, event)
            else:
                result = {"success": False, "msg": "Neither of these accounts are managed by this bank"}
        return result

    @staticmethod
    def get_exchange_history(account_no, auth_token) -> list:
        # using an account number, retrieve all exchanges involving that account to date
        requesting_user_id = auth_token["user_id"]
        user_is_manager = auth_token.get("manager_id", False)
        target_account = Accounts.objects.filter(account_number=account_no).first()

        if target_account is None:
            return {"success": False, "msg": "the accounts specified does not exist"}

        if target_account.owner_id == requesting_user_id or user_is_manager:
            exchange_records = ExchangeHistory.objects.filter((Q(to_account_no=account_no, to_routing_no=settings.BANK_ROUTING_NUMBER)|
                                                               Q(from_account_no=account_no, from_routing_no=settings.BANK_ROUTING_NUMBER)))
            serialized_records = json.loads(serializers.serialize("json", exchange_records))
            for record in serialized_records: record["fields"]["pk"] = record["pk"]
            serialized_records = list(map(lambda x: x["fields"], serialized_records))
            for i, record in enumerate(serialized_records):
                if (int(record["from_account_no"]) == target_account.account_number and
                int(record["from_routing_no"]) == settings.BANK_ROUTING_NUMBER):
                    record["amount"] = str(-Decimal(record["amount"]))

            return {"success": True, "data": serialized_records}

        else:
            return {"success": False, "msg": "insufficient permission"}
