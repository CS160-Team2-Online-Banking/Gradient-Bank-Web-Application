from bankapi.models import *
from django.db import transaction
from django.core import serializers
from bankapi.transfer.exchange_processor import ExchangeProcessor
import json

class AccountProcess:
    # looks up id in account db,
    @staticmethod
    def account_lookup(decrypted_auth_token, account_no_to_lookup=None) -> dict:
        owner_id = decrypted_auth_token["user_id"]
        owner = Customer.objects.filter(pk=owner_id).first()

        if owner_id is None:
            return {"success": False, "msg": "Error: no such customer exists"}

        if account_no_to_lookup is None:
            # return all accounts belonging to this user, but omit exchange history details
            # (we'll need to append the account type still)
            accounts = Accounts.objects.filter(owner_id=owner.pk)
            json_arr = json.loads(serializers.serialize("json", accounts))
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
            json_arr = list(map(lambda x: x["fields"], json_arr))

            for i, entry in enumerate(json_arr):
                entry["exchange_history"] = exchange_history

            return {"success": True, "data": json_arr}


    def account_add(self, decrypted_auth_token, data):
        pass

    def account_update(self, decrypted_auth_token, data):
        pass
