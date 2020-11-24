from django.db import transaction
from django.core import serializers
from bankapi.transfer.exchange_processor import ExchangeProcessor
from bankapi.models import *
import json


class AccountProcess:
    def __init__(self, data=None):
        if data is not None:
            self.account = data["account_id"]
            self.balance = data["balance"]
            self.account_number = data["account_number"]
            self.account_type = data["account_type"]
            self.owner = data["owner_id"]
        # ip information should also be collected here

    @staticmethod
    def account_lookup(decrypted_auth_token, account_no_to_lookup=None) -> dict:
        owner_id = decrypted_auth_token["user_id"]
        manager_id = decrypted_auth_token.get("manager_id", None)
        owner = Customer.objects.filter(pk=owner_id).first()

        if owner is None and manager_id is None:  # this will not die if there is a manager id
            return {"success": False, "msg": "Error: no such customer exists"}

        if account_no_to_lookup is None and owner is not None:
            # return all accounts belonging to this user, but omit exchange history details
            # (we'll need to append the account type still)
            accounts = Accounts.objects.filter(owner_id=owner.pk)
            json_arr = json.loads(serializers.serialize("json", accounts))
            for record in json_arr: record["fields"]["pk"] = record["pk"]
            json_arr = list(map(lambda x: x["fields"], json_arr))

            for i, entry in enumerate(json_arr):
                account_type_id = int(entry["account_type"])
                account_type = AccountTypes.objects.get(pk=account_type_id)
                entry["account_type"] = {"account_type_id": account_type.pk,
                                         "account_type_name": account_type.account_type_name}
            return {"success": True, "data": json_arr}
        else:
            # return one specific account along with it's exchange history
            accounts = Accounts.objects.filter(owner_id=owner.pk, account_number=account_no_to_lookup)
            result = ExchangeProcessor.get_exchange_history(account_no_to_lookup, decrypted_auth_token)
            exchange_history = list()
            if result["success"]:
                exchange_history = result["data"]

            json_arr = json.loads(serializers.serialize("json", accounts))
            for record in json_arr: record["fields"]["pk"] = record["pk"]
            json_arr = list(map(lambda x: x["fields"], json_arr))

            for i, entry in enumerate(json_arr):
                account_type_id = int(entry["account_type"])
                account_type = AccountTypes.objects.get(pk=account_type_id)
                entry["account_type"] = {"account_type_id": account_type.pk,
                                         "account_type_name": account_type.account_type_name}
            for i, entry in enumerate(json_arr):
                entry["exchange_history"] = exchange_history

            return {"success": True, "data": json_arr}

    @staticmethod
    @transaction.atomic(using="bank_data")
    def account_add(decrypted_auth_token, data) -> bool:
        requesting_user_id = decrypted_auth_token["user_id"]
        requesters_account = Customer.objects.filter(pk=requesting_user_id).first()

        if requesters_account is None:
            return {"success": False, "msg": "Error: no such customer exists"}

        if Accounts.objects.filter(account_number=1337_0000_0000).first() is None:
            new_account_number = 1337_0000_0000
        else:
            new_account_number = Accounts.objects.latest("account_number").account_number + 1

        account_type = AccountTypes.objects.filter(account_type_name=data["account_type"]).first()
        if account_type is None:
            return {"success": False, "msg": "Error: Invalid account type"}

        new_account = Accounts(balance=0,
                               account_number=new_account_number,
                               account_type=account_type,
                               owner_id=requesters_account.pk)
        new_account.save()
        return {"success": True, "data": {"account_no": new_account.account_number, "account_id": new_account.pk}}

    # redundant, just use account_lookup
    def get_account_info(self) -> dict:
        pass

    @staticmethod
    @transaction.atomic(using="bank_data")
    def close_account(decrypted_auth_token, data):
        owner_id = decrypted_auth_token["user_id"]
        account_number = data["account_number"]

        owner = Customer.objects.filter(pk=owner_id).first()
        if owner is None:
            return {"success": False, "msg": "Error: no such customer exists"}

        account = Accounts.objects.filter(account_number=account_number, owner_id=owner.pk).first()
        if account is None:
            return {"success": False, "msg": "Error: no such account exists"}

        if account.balance == 0:
            account.owner_id = 0
            account.save()
            # delete all autopayments as well
            autopayments = AutopaymentObjects.objects.filter(owner_user_id=owner.pk, from_account_id=account.pk).delete()
            return {"success": True, "data": {"account_id": account.pk}}
        else:
            return {"success": False, "msg": "Error: you cannot close an account while it still has an active balance"}
