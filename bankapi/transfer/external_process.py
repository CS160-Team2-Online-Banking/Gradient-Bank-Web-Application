from bankapi.transfer.transfer_process import TransferProcess
import bankapi.models as bankmodels
from decimal import *
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Now

TRANSFER_QUEUE_EVENT_ID = bankmodels.EventTypes.objects.get(name="TRANSFER QUEUED").pk
TRANSFER_CANCEL_EVENT_ID = bankmodels.EventTypes.objects.get(name="TRANSFER CANCELED").pk

class ExternalTransfer(TransferProcess):
    def __init__(self, data=None):
        if data is not None:
            self.to_account = data["to_account_id"]
            self.from_account = data["from_account_id"]
            self.amount = data["amount"]
            self.eventInfo = data["event_info"]
        # ip information should also be collected here

    @transaction.atomic
    def queue_transfer(self, decrypted_auth_token):
        pass

    def get_transfer_info(self):
        data = dict()
        data["to_account"] = self.to_account
        data["from_account"] = self.from_account
        data["amount"] = self.amount
        return data

    @transaction.atomic
    def process_transfer(self, transfer_id):
        pass

