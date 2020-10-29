from django.db import transaction
from bankapi.models import *


class TransferValidator:
    def verify_transfer(self, transfer_info, authentication_token) -> bool:
        pass


class ExternalValidator(TransferValidator):
    @transaction.atomic
    def verify_transfer(self, transfer_info, authentication_token):
        request_user_id = authentication_token["user_id"]
        from_results = Accounts.objects.filter(pk=transfer_info["from_account"])
        to_results = Accounts.objects.filter(pk=transfer_info["to_account"])
        if len(from_results) and len(to_results):
            from_owner_id = from_results.first().owner_id
            to_owner_id = to_results.first().owner_id
        else:
            return False
        return from_owner_id == to_owner_id == request_user_id


class InternalValidator(TransferValidator):
    @transaction.atomic
    def verify_transfer(self, transfer_info, authentication_token):
        request_user_id = authentication_token["user_id"]
        from_results = Accounts.objects.filter(pk=self.from_account)
        if len(from_results):
            from_owner_id = from_results.first().owner_id
        else:
            return False
        return request_user_id == from_owner_id
