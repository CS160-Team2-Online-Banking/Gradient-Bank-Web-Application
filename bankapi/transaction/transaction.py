from django.db import transaction
from bankapi.models import *


class TransactionProcess:
    def queue_transaction(self, transaction_data):
        pass

    def process_transaction(self, transaction_id=None):
        pass