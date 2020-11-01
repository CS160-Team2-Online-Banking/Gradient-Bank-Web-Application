from django.core.management.base import BaseCommand, CommandError
from bankapi.models import *
from bankapi.autopayment.autopayment import *
from bankapi.transfer.internal_process import *
from datetime import datetime
from bankapi.transfer.external_process import *
from bankapi.utils.network_utils import *
from django.db.models.functions import Now

class Command(BaseCommand):
    help = 'run to process autopayments'

    def handle(self, *args, **options):
        autopayment_objects = AutopaymentObjects.objects.all()
        for auto_obj in autopayment_objects:
            if is_payment_due(auto_obj):  # if we are due to make a payment
                transfer_type = auto_obj.transfer_type

                if transfer_type == TransferTypes.EXTERN:
                    transfer_handler = InternalTransfer({"to_account_id": auto_obj.to_account_id,
                                                         "to_account_no": None,
                                                         "from_account_id": auto_obj.from_account_id,
                                                         "from_account_no": None,
                                                         "amount": auto_obj.transfer_amount,
                                                         "event_info": {
                                                             "request_ip4": 0,
                                                             "request_ip6": 0,
                                                             "request_time": get_utc_now_str()
                                                         }})

                else:
                    transfer_handler = ExternalTransfer({"to_account_id": auto_obj.to_account_id,
                                                         "to_account_no": None,
                                                         "from_account_id": auto_obj.from_account_id,
                                                         "from_account_no": None,
                                                         "amount": auto_obj.transfer_amount,
                                                         "event_info": {
                                                             "request_ip4": 0,
                                                             "request_ip6": 0,
                                                             "request_time": get_utc_now_str()
                                                         }})
                print('preparing for transfer')
                with transaction.atomic():
                    result = transfer_handler.queue_transfer({"user_id": auto_obj.owner_user_id})
                    if result:  # if the payment went through
                        auto_obj.last_payment = Now()
                        auto_obj.save()



