from bankapi.transfer.transfer_process import TransferProcess
from bankapi.models import *
from decimal import *
from bankapi.utils.network_utils import build_event
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Now


class InternalTransfer(TransferProcess):
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
            return False  # TODO: handle this, raise an exception or something

        transfer_type = TransferTypes.A_TO_A if from_owner_id == to_owner_id else TransferTypes.U_TO_U

        # check for authenticity
        # add the transfer to the queue, otherwise don't add it
        # beyond this point, it will be considered an authentic request
        if requesting_user_id == from_owner_id:
            # add the transfer to the transfers table, and queue it's id to the
            new_event = build_event(requesting_user_id, 0, 0, TRANSFER_QUEUE_EVENT_ID, request_time)
            new_event.save()
            new_transfer = Transfers(to_account_id=to_results.first().pk,
                                     from_account_id=from_results.first().pk,
                                     transfer_type=transfer_type,
                                     amount=self.amount,
                                     create_event_id=new_event.pk,
                                     time_stamp=Now())
            new_transfer.save()
            queue_ticket = PendingTransfersQueue(transfer_id=new_transfer.pk,
                                                 added=Now())
            queue_ticket.save()
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
        transfer = Transfers.objects.filter(pk=transfer_id).first()
        if transfer is None:
            return False  # TODO: handle this, raise an exception or something

        from_account = Accounts.objects.filter(pk=transfer.from_account_id).first()
        if from_account is None:
            return False  # TODO: handle this, raise an exception or something

        to_account = Accounts.objects.filter(pk=transfer.to_account_id).first()
        if to_account is None:
            return False  # TODO: handle this, raise an exception or something

        pending_transfer = PendingTransfersQueue.objects.filter(pk=transfer.pk).first()
        if pending_transfer is None:
            return False  # TODO: handle this, raise an exception or something

        amount = transfer.amount
        if transfer.amount <= from_account.balance:
            from_account.balance = from_account.balance-amount
            to_account.balance = to_account.balance+amount
            from_account.save()
            to_account.save()

            new_completed_record = CompletedTransfersLog(transfer_id=pending_transfer.pk,
                                                         completed=Now(),
                                                         started=pending_transfer.added)
            pending_transfer.delete()
            new_completed_record.save()
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
