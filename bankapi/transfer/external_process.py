from bankapi.transfer.transfer_process import TransferProcess
from bankapi.models import *
from bankapi.utils.network_utils import build_event
from decimal import *
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Now


class ExternalTransfer(TransferProcess):
    def __init__(self, data=None):
        if data is not None:
            self.to_account = data["to_account_id"]
            self.to_account_no = data["to_account_no"]
            self.from_account = data["from_account_id"]
            self.from_account_no = data["from_account_no"]
            self.amount = data["amount"]
            self.eventInfo = data["event_info"]

            if ((self.to_account is None and self.to_account_no is None) or
               (self.from_account is None and self.from_account_no is None)):
                raise ValueError("Either an account number or id must be specified")
        # ip information should also be collected here

    @transaction.atomic
    def queue_transfer(self, decrypted_auth_token):
        requesting_user_id = decrypted_auth_token["user_id"]
        request_ip4 = self.eventInfo["request_ip4"]
        request_ip6 = self.eventInfo["request_ip6"]
        request_time = self.eventInfo["request_time"]

        if self.from_account is not None:
            from_results = Accounts.objects.filter(pk=self.from_account)
        else:
            from_results = Accounts.objects.filter(account_number=self.from_account_no)

        if self.to_account is not None:
            to_results = Accounts.objects.filter(pk=self.to_account)
        else:
            to_results = Accounts.objects.filter(account_number=self.to_account_no)
        if len(from_results) and len(to_results):
            from_owner_id = from_results.first().owner_id
            to_owner_id = to_results.first().owner_id
        else:
            return False  # we cannot schedule a transfer to accounts that aren't registered

        # check for authenticity
        # add the transfer to the queue, otherwise don't add it
        # beyond this point, it will be considered an authentic request
        if requesting_user_id == from_owner_id == to_owner_id:
            new_event = build_event(requesting_user_id, 0, 0, TRANSFER_QUEUE_EVENT_ID, request_time)
            new_event.save()
            new_transfer = Transfers(to_account_id=to_results.first().pk,
                                     from_account_id=from_results.first().pk,
                                     transfer_type="EXTERN",
                                     amount=self.amount,
                                     create_event_id=new_event.pk,
                                     time_stamp=Now())
            new_transfer.save()
            pending_transfer = PendingTransfersQueue(transfer_id=new_transfer.pk,
                                                     added=Now())
            pending_transfer.save()
            return True
        return False

    def get_transfer_info(self):
        data = dict()
        data["to_account"] = self.to_account
        data["from_account"] = self.from_account
        data["amount"] = self.amount
        return data

    @transaction.atomic
    def process_transfer(self, transfer_id=None):
        # verify (again) that the external account exists
        # verify that there's enough money in the from account to make the transfer
        # subtract the money from the internal account
        # add an entry to the external transfer pool
        # move the transfer from pending to complete
        transfer = Transfers.objects.filter(pk=transfer_id).first()
        if transfer is None:
            return False  # TODO: handle this, raise an exception or something

        external_account = ExternalAccounts.objects.filter(pk=transfer.to_account_id).first()
        internal_account = Accounts.objects.filter(pk=transfer.from_account_id).first()
        if (external_account is None) or (internal_account is None):
            return False  # TODO: handle this, raise an exception or something
        pending_transfer = PendingTransfersQueue.objects.filter(pk=transfer_id).first()
        if pending_transfer is None:
            return False  # TODO: handle this, raise an exception or something

        _amount = transfer.amount
        if transfer.amount <= internal_account.balance:
            internal_account.balance = internal_account.balance - _amount
            internal_account.save()
            external_queue_object = ExternalTransferPool(internal_account_id=internal_account.pk,
                                                         external_account_id=external_account.pk,
                                                         amount=_amount,
                                                         inbound=False)
            external_queue_object.save()
            completed_transfer = CompletedTransfersLog(transfer_id=transfer.pk,
                                                       completed=Now(),
                                                       started=pending_transfer.added)
            pending_transfer.delete()
            completed_transfer.save()
            return True
        return False

    @transaction.atomic
    def cancel_transfer(self, transfer_id=None):
        pending_transfer = PendingTransfersQueue.object.filter(pk=transfer_id).first()
        transfer = Transfers.objects.filter(pk=transfer_id).first()
        if pending_transfer is not None:
            failed_transaction = FailedTransfers(transfer_id=transfer.pk,
                                                 started=pending_transfer.added,
                                                 failed=Now())
            failed_transaction.save()
            pending_transfer.delete()




