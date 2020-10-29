from django.core.management.base import BaseCommand, CommandError
from bankapi.models import *
from bankapi.transfer.internal_process import *
from bankapi.transfer.external_process import *

class Command(BaseCommand):
    help = 'processes a transfer request from the queue'

    def handle(self, *args, **options):
        # pull an entry from the transfers table
        # determine what type of transfer needs to happen
        top_transfer = PendingTransfersQueue.objects.all().first()
        if top_transfer is None:
            return
        transfer_id = top_transfer.pk
        transfer_data = Transfers.objects.filter(pk=transfer_id).first()
        # TODO: if top_transfer is empty, or there are no pending transfers, exit
        transfer_type = transfer_data.transfer_type
        transfer_handler = None
        if transfer_type == 'U_TO_U' or transfer_type == 'A_TO_A':
            transfer_handler = InternalTransfer()
        elif transfer_type == 'EXTERNAL':
            transfer_handler = ExternalTransfer()

        result = transfer_handler.process_transfer(transfer_id)
        if result:
            pass
        else:  # if the transfer failed, delete it
            transfer_handler.cancel_transfer(transfer_id)
        # TODO: detect when transfers failed, and cancel them
