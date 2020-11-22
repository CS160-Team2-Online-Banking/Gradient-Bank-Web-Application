from django.db import transaction
from django.db.models.functions import Now
from bankapi.models import *


class TransactionProcess:
    def __init__(self, transaction_data):
        self.card_account_number = transaction_data["card_account_number"]
        self.merchant_id = transaction_data["merchant_id"]
        self.card_network_id = transaction_data["card_network_id"]
        self.amount = transaction_data["amount"]
        self.time_stamp = transaction_data["time_stamp"]

    @transaction.atomic(using="bank_data")
    def queue_transaction(self, authentication_token):
        requesting_network_id = authentication_token["network_id"]

        account = Accounts.objects.filter(account_number=self.card_account_number).first()
        if account is None:  # verify the account is
            return False  # TODO: handle this, raise an exception or something

        payment_network = PaymentNetworks.objects.filter(pk=self.card_network_id).first()
        if payment_network is None:
            return False  # TODO: handle this, raise an exception or something
        if (account.account_type_id == CHECKING_ACCOUNT_ID and
            payment_network.network_GID == requesting_network_id):
            new_transaction = Transactions(card_account_id=account.pk,
                                           merchant_id=self.merchant_id,
                                           card_network_id=payment_network.pk,
                                           amount=self.amount,
                                           time_stamp=self.time_stamp)
            new_transaction.save()
            pending_transaction = PendingTransactionsQueue(transaction_id=new_transaction.pk,
                                                           added=Now())
            pending_transaction.save()
            return True
        return False

    @transaction.atomic(using="bank_data")
    def process_transaction(self, transaction_id=None):
        pending_transaction = PendingTransactionsQueue.objects.filter(pk=transaction_id).first()
        if pending_transaction is None:
            return False  # TODO: handle this, raise an exception or something

        transaction_result = Transactions.objects.filter(pk=transaction_id).first()
        if transaction_result is None:
            return False  # TODO: handle this, raise an exception or something

        account = transaction_result.card_account

        if transaction_result.amount <= account.balance:
            account.balance = account.balance - transaction_result.amount
            account.save()

            completed_transaction = CompletedTransactionsLog(transaction_id=transaction_result.pk,
                                                             started=pending_transaction.added,
                                                             completed=Now())
            pending_transaction.delete()
            completed_transaction.save()
            return True
        return False

    @transaction.atomic(using="bank_data")
    def cancel_transaction(self, transaction_id=None):
        pending_transaction = PendingTransactionsQueue.object.filter(pk=transaction_id).first()
        transaction_data = Transactions.objects.filter(pk=transaction_id).first()
        if pending_transaction is not None:
            failed_transaction = FailedTransfers(transaction_id=transaction_data.pk,
                                                 started=pending_transaction.added,
                                                 failed=Now())
            failed_transaction.save()
            pending_transaction.delete()