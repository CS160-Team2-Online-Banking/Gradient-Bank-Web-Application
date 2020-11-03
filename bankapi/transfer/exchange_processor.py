from bankapi.models import *
from bankapi.utils.network_utils import build_event
from decimal import *
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Now


@transaction.atomic
def external_transfer_handler(auth_token, from_account_no, to_account_no, to_routing_no, amount) -> dict:
    user_id = auth_token["user_id"]
    from_account = Accounts.objects.filter(account_number=from_account_no).first()
    if amount <= 0:
        return {"success": False, "msg": "you can only transfer non-zero positive sums of money"}
    if from_account is None:
        return {"success": False, "msg": "one of the accounts specified does not exist"}

    owner_id = from_account.owner_id

    if owner_id == user_id:
        if amount <= from_account.balance:
            from_account.balance = from_account.balance - amount
            from_account.save()

            ex = ExchangeHistory(to_account_no=to_account_no,
                                 from_account_no=from_account_no,
                                 to_routing_no=to_routing_no,
                                 from_routing_no=settings.BANK_ROUTING_NUMBER,
                                 amount=amount,
                                 posted=Now(),
                                 status=ExchangeHistory.ExchangeHistoryStatus.POSTED)
            ex.save()
            ext_pool = ExternalTransferPool(internal_account=from_account,
                                            external_account_routing_no=to_routing_no,
                                            external_account_no=to_account_no,
                                            amount=amount,
                                            inbound=False,
                                            debit=False,
                                            exchange_obj=ex)
            ext_pool.save()
            return {"success": True, "data": {"transfer_id": ex.pk}}
        else:
            return {"success": False, "msg": "insufficient funds"}
        return {"success": False, "msg": "insufficient permission"}


@transaction.atomic
def internal_transfer_handler(auth_token, from_account_no, to_account_no, amount) -> dict:
    user_id = auth_token["user_id"]
    from_account = Accounts.objects.filter(account_number=from_account_no).first()
    to_account = Accounts.objects.filter(account_number=to_account_no).first()

    if amount <= 0:
        return {"success": False, "msg": "you can only transfer non-zero positive sums of money"}
    if from_account is None or to_account is None:
        return {"success": False, "msg": "one of the accounts specified does not exist"}

    owner_id = from_account.owner_id

    if owner_id == user_id:
        if amount <= from_account.balance:
            from_account.balance = from_account.balance - amount
            to_account.balance = to_account.balance + amount
            from_account.save()
            to_account.save()

            ex = ExchangeHistory(to_account_no=to_account_no,
                                 from_account_no=from_account_no,
                                 to_routing_no=settings.BANK_ROUTING_NUMBER,
                                 from_routing_no=settings.BANK_ROUTING_NUMBER,
                                 amount=amount,
                                 posted=Now(),
                                 finished=Now(),
                                 status=ExchangeHistory.ExchangeHistoryStatus.FINISHED)
            ex.save()
            return {"success": True, "data": {"transfer_id": ex.pk}}
        else:
            return {"success": False, "msg": "insufficient funds"}
    return {"success": False, "msg": "insufficient permission"}


@transaction.atomic
def deposit_handler(auth_token, from_account_no, from_routing_no, to_account_no, amount) -> dict:
    requesting_user_id = auth_token["user_id"]
    debit_authorization_key = auth_token["debit_auth_key"]

    to_account = Accounts.objects.filter(account_number=to_account_no).first()

    if amount <= 0:
        return {"success": False, "msg": "you can only deposit non-zero positive sums of money"}
    if to_account is None:
        return {"success": False, "msg": "one of the accounts specified does not exist"}

    to_owner_id = to_account.owner_id

    if requesting_user_id == to_owner_id and debit_authorization_key == settings.DEBIT_AUTH_KEY:
        ex = ExchangeHistory(to_account_no=to_account_no,
                             from_account_no=from_account_no,
                             to_routing_no=settings.BANK_ROUTING_NUMBER,
                             from_routing_no=settings.BANK_ROUTING_NUMBER,
                             amount=amount,
                             posted=Now(),
                             type=ExchangeHistory.ExchangeTypes.DEPOSIT,
                             status=ExchangeHistory.ExchangeHistoryStatus.POSTED)
        ex.save()
        ext_pool = ExternalTransferPool(internal_account=to_account,
                                        external_account_routing_no=from_routing_no,
                                        external_account_no=from_account_no,
                                        amount=amount,
                                        inbound=True,
                                        debit=True,
                                        exchange_obj=ex)
        ext_pool.save()
        return {"success": True, "data": {"transfer_id": ex.pk}}
    return {"success": False, "msg": "insufficient permission"}

class ExchangeProcessor:
    @staticmethod
    def start_exchange(exchange_data, auth_token) -> dict:
        # the first step is to determine how to route the money
        # if it's some kind of external transfer, we need to move the money to or from a pool
        # if it's an internal transfer, we just need to move the money over (we can do this right here and be done
        to_account_no = exchange_data["to_account_no"]
        to_routing_no = exchange_data["to_routing_no"]
        from_account_no = exchange_data["from_account_no"]
        from_routing_no = exchange_data["from_routing_no"]
        amount = exchange_data["amount"]
        if from_routing_no == settings.BANK_ROUTING_NUMBER:
            if to_routing_no == settings.BANK_ROUTING_NUMBER:
                result = internal_transfer_handler(auth_token, from_account_no, to_account_no, amount)
            else:
                result = external_transfer_handler(auth_token, from_account_no, to_account_no, to_routing_no, amount)
        else:
            if to_routing_no == settings.BANK_ROUTING_NUMBER:
                result = deposit_handler(auth_token, from_account_no, from_routing_no, to_account_no, amount)
            else:
                result = {"success": False, "msg": "Neither of these accounts are managed by this bank"}
        return result
