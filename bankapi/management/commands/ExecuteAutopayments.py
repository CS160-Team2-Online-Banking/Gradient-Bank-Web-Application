from django.core.management.base import BaseCommand, CommandError
from bankapi.models import *
from bankapi.autopayment.autopayment import *
from bankapi.transfer.exchange_processor import *
from django.conf import settings
from datetime import datetime
from bankapi.utils.network_utils import *
from django.db.models.functions import Now

class Command(BaseCommand):
    help = 'run to process autopayments'

    def handle(self, *args, **options):
        autopayment_objects = AutopaymentObjects.objects.all()
        for auto_obj in autopayment_objects:
            if is_payment_due(auto_obj):  # if we are due to make a payment

                data = {"to_account_no": auto_obj.to_account_no,
                        "to_routing_no": auto_obj.to_routing_no,
                        "from_account_no": auto_obj.from_account.account_number,
                        "from_routing_no": settings.BANK_ROUTING_NUMBER,
                        "amount": auto_obj.transfer_amount}

                print('preparing for transfer for autopayment {autopayment}'.format(autopayment=auto_obj.pk))
                with transaction.atomic(using='bank_data'):
                    result = ExchangeProcessor.start_exchange(data, {"user_id": auto_obj.owner_user_id})
                    if result["success"]:  # if the payment went through
                        auto_obj.last_payment = Now()
                        auto_obj.save()



