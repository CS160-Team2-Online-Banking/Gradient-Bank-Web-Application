from api.transfer.transfer_process import TransferProcess
from django.db import transaction

class InternalTransfer(TransferProcess):
    def __init__(self, data):
        self.to_account = data["to_account_id"]
        self.from_account = data["from_account_id"]
        self.amount = data["amount"]
        # ip information should also be collected here

    def queue_transfer(self, auth_token):
        # check for validity and authenticity
        # add the transfer to the queue, otherwise don't add it
        # beyond this point, it will be considered an authentic request
        # add the transfer to the transfers table, and queue it's id to the
        pass

    def get_transfer_info(self):
        data = dict()
        data["to_account"] = self.to_account
        data["from_account"] = self.from_account
        data["amount"] = self.amount
        return data

    def process_transfer(self):
        # open the sql connection
        # start a transaction where:
            # you subract the amount from one account
            # add it to another
            # commit only if the balance of the from account isn't negative
        # commit or revert the transaction
        # remove the transfer from the pending log and move to completed if we commit
        pass
