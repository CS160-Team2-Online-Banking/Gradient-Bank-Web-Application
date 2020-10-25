
class TransferProcess:
    def process_transfer(self, transfer_id):
        # called from the list of transfer requests
        # contains all business logic needed to validate the request
        pass

    def queue_transfer(self, decrypted_auth_token):
        # called when a transfer request is made
        # should validate the request using the provided authentication request
        # further validation to ensure the request should be done using the transfer validator
        pass

    def get_transfer_info(self) -> dict:
        # returns a dictionary of data about this transfer request
        pass
