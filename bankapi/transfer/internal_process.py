from bankapi.transfer.transfer_process import TransferProcess
import bankapi.models as bankmodels
from decimal import *
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Now

TRANSFER_QUEUE_EVENT_ID = bankmodels.EventTypes.objects.get(name="TRANSFER QUEUED").pk
TRANSFER_CANCEL_EVENT_ID = bankmodels.EventTypes.objects.get(name="TRANSFER CANCELED").pk


class InternalTransfer(TransferProcess):
    def __init__(self, data=None):
        if data is not None:
            self.to_account = data["to_account_id"]
            self.from_account = data["from_account_id"]
            self.amount = data["amount"]
            self.eventInfo = data["event_info"]
        # ip information should also be collected here

    @transaction.atomic
    def queue_transfer(self, decrypted_auth_token):
        requesting_user_id = decrypted_auth_token["user_id"]
        request_ip4 = self.eventInfo["request_ip4"]
        request_ip6 = self.eventInfo["request_ip6"]
        request_time = self.eventInfo["request_time"]
        from_owner_id = bankmodels.Accounts.objects.get(pk=self.from_account).owner_id
        to_owner_id = bankmodels.Accounts.objects.get(pk=self.to_account).owner_id
        transfer_type = "A_TO_A" if from_owner_id == to_owner_id else "U_TO_U"

        # check for authenticity
        # add the transfer to the queue, otherwise don't add it
        # beyond this point, it will be considered an authentic request
        if requesting_user_id == from_owner_id:
            # add the transfer to the transfers table, and queue it's id to the
            new_event = bankmodels.EventLog(intiator_user_id=requesting_user_id,
                                            ip6_address=request_ip6,
                                            ip4_address=request_ip4,
                                            event_type=TRANSFER_QUEUE_EVENT_ID,
                                            event_time=request_time)
            new_event.save()

            new_transfer = bankmodels.Transfers(to_account_id=self.to_account,
                                                from_account_id=self.from_account,
                                                transfer_type=transfer_type,
                                                amount=self.amount,
                                                create_event_id=new_event.pk,
                                                time_stamp=Now())
            new_transfer.save()
            queue_ticket = bankmodels.PendingTransfersQueue(transfer_id=new_transfer.pk,
                                                            added=Now())
            queue_ticket.save()



    def get_transfer_info(self):
        data = dict()
        data["to_account"] = self.to_account
        data["from_account"] = self.from_account
        data["amount"] = self.amount
        return data

    @transaction.atomic
    def process_transfer(self, transfer_id=None):
        transfer = bankmodels.Transfers.objects.get(pk=transfer_id)
        from_account = bankmodels.Accounts.objects.get(pk=transfer.from_account_id)
        to_account = bankmodels.Accounts.objects.get(pk=transfer.to_account_id)
        amount = transfer.amount
        if transfer.amount <= from_account.balance:
            from_account.balance = from_account.balance-amount
            to_account.balance = to_account.balance+amount
            from_account.save()
            to_account.save()

            pending_transfer = bankmodels.PendingTransfersQueue.objects.get(pk=transfer.pk)
            new_completed_record = bankmodels.CompletedTransfersLog(transfer_id=pending_transfer.pk,
                                                                    completed=Now(),
                                                                    started=pending_transfer.added)
            pending_transfer.delete()
            new_completed_record.save()



