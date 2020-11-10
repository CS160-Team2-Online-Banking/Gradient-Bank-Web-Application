from django.db import *
from django.db import transaction

from bankapi.models import *


class AccountProcess:
    def __init__(self, data=None):
        if data is not None:
            self.account = data["account_id"]
            self.balance = data["balance"]
            self.account_number = data["account_number"]
            self.account_type = data["account_type"]
            self.owner = data["owner_id"]
        # ip information should also be collected here

    @transaction.atomic
    def account_add(self, decrypted_auth_token, data) -> bool:
        requesting_user_id = decrypted_auth_token["user_id"]
        requesters_account = Customer.objects.filter(pk=requesting_user_id).first()

        if requesters_account is None:
            return False  # TODO: handle this, raise an exception or something

        if Accounts.objects.filter(account_number=1337_0000_0000).first() is None:
            new_account_number = 1337_0000_0000
        else:
            new_account_number = Accounts.objects.latest("account_number").account_number + 1

        # TODO: data sanitation for account addition
        new_account = Accounts(account_id=new_account_number,
                               balance=0,
                               account_number=new_account_number,
                               account_type=data.account_type,
                               owner=requesters_account.pk
                               )
        new_account.save()
        return True;

    # redundant, just use account_lookup
    def get_account_info(self) -> dict:
        pass
