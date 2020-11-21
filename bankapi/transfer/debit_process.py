from bankapi.transfer.transfer_process import TransferProcess
from bankapi.models import *
from decimal import *
from bankapi.utils.network_utils import build_event
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Now
from django.conf import settings


class DebitProcess:
    def __init__(self, data=None):
        if data is not None:
            self.to_account_no = data["to_account_no"]
            self.from_routing_no = data["to_routing_no"]
            self.from_account_no = data["from_account_no"]
            self.amount = data["amount"]
            self.eventInfo = data["event_info"]

    @transaction.atomic(using="bank_data")
    def queue_debit(self, decrypted_auth_token):
        requesting_user_id = decrypted_auth_token["user_id"]
        debit_authorization_key = decrypted_auth_token["debit_auth_key"]
        request_ip4 = self.eventInfo["request_ip4"]
        request_ip6 = self.eventInfo["request_ip6"]
        request_time = self.eventInfo["request_time"]

        to_result = Accounts.filter(account_number=self.to_account_no).first()

        if to_result is not None:
            to_owner_id = to_result.owner_id
        else:
            return False

        if requesting_user_id == to_owner_id and debit_authorization_key == settings.DEBIT_AUTH_KEY:
            external_process = ExternalTransferPool(internal_account=to_result,
                                                    external_account_no=self.from_account_no,
                                                    external_account_routing_no=self.from_routing_no,
                                                    amount=self.amount,
                                                    inbound=True,
                                                    debit=True)
            external_process.save()

            new_debit_hist = DebitHistory(debit_intiator_id=to_result.owner_id,
                                          from_account_no=self.from_account_no,
                                          from_routing_no=self.from_routing_no,
                                          to_account=self.to_result,
                                          amount=self.amount,
                                          time_started=Now(),
                                          pending_queue_obj=external_process)
            new_debit_hist.save()

            new_event = build_event(requesting_user_id, 0, 0, DEBIT_QUEUED_EVENT_ID, request_time)
            new_event.data_id = new_debit_hist.pk
            new_event.save()

            return True
        return False

    @staticmethod
    @transaction.atomic(using="bank_data")
    def approve_debit(debit_id=None):
        if debit_id:
            debit_obj = DebitHistory.objects.filter(pk=debit_id).first()
            if debit_obj is None:
                return False

            if debit_obj.pending_queue_obj is None:
                return False

            queue_obj = debit_obj.pending_queue_obj
            internal_account = queue_obj.internal_account
            internal_account.amount = internal_account.amount + queue_obj.amount

            internal_account.save()
            queue_obj.delete()  # this should set the pending_id to null
            debit_obj.time_processed = Now()
            debit_obj.status = "COMPLETED"
            debit_obj.save()
            return True

    @staticmethod
    @transaction.atomic(using="bank_data")
    def decline_debit(debit_id=None):
        if debit_id:
            debit_obj = DebitHistory.objects.filter(pk=debit_id).first()
            if debit_obj is None:
                return False

            if debit_obj.pending_queue_obj is None:
                return False

            queue_obj = debit_obj.pending_queue_obj

            queue_obj.delete()  # this should set the pending_id to null
            debit_obj.time_processed = Now()
            debit_obj.status = "DECLINED"
            debit_obj.save()
            return True





