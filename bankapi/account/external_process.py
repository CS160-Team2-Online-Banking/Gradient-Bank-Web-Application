from django.db import *
from bankapi.account.account_process import AccountProcess
from bankapi.models import *

class ExternalAccount(AccountProcess):
    #TODO: This is just a straight copy paste of the internal process file, need to differentiate the two
    def __init__(self, data=None):
        if data is not None:
            self.account = data["account_id"]
            self.balance = data["balance"]
            self.account_number = data["account_number"]
            self.account_type = data["account_type"]
            self.owner = data["owner_id"]
        # ip information should also be collected here

            def get_account_info(self):
                # TODO: verify that this method does not compromise security
                data = dict()
                data["account_id"] = self.account
                data["balance"] = self.balance
                data["account_number"] = self.account_number
                data["account_type"] = self.account_type
                data["owner"] = self.owner
                return data

            def account_lookup(self, account_id_to_lookup, decrypted_auth_token):
                # need to check for authorization to do this
                requesting_user_id = decrypted_auth_token["user_id"]
                request_ip4 = self.eventInfo["request_ip4"]
                request_ip6 = self.eventInfo["request_ip6"]
                request_time = self.eventInfo["request_time"]

                lookup_account = Accounts.objects.filter(pk=account_id_to_lookup).first()
                this_accounts_id = self.account
                requesters_account = Accounts.objects.filter(pk=requesting_user_id).first()
                if len(lookup_account) and len(requesters_account):
                    requesters_type_id = requesters_account.account_type
                    requesters_type = AccountTypes.objects.filter(pk=requesters_type_id)
                    if len(requesters_type):
                        requesters_type = requesters_type.account_type_name
                    else:
                        return False  # TODO: handle this, raise an exception or something
                else:
                    return False  # TODO: handle this, raise an exception or something

                account_data = dict()
                # case where the requester is looking for their own information
                if len(requesting_user_id) and len(this_accounts_id) and len(account_id_to_lookup) and \
                        this_accounts_id == requesting_user_id and this_accounts_id == account_id_to_lookup:
                    account_data["account_id"] = lookup_account.account_id
                    account_data["balance"] = lookup_account.balance
                    account_data["account_number"] = lookup_account.account_number
                    account_data["account_type"] = lookup_account.account_type
                    account_data["owner"] = lookup_account.owner
                elif len(requesting_user_id) and len(this_accounts_id) and len(
                        account_id_to_lookup) and requesters_type == "bank_manager":
                    # bank manager requesting information, so it's authorized
                    # TODO: NEED TO CHANGE THE REQUESTER TYPE CHECK -> do data sanitation and check for different cases/spacing between
                    account_data["account_id"] = lookup_account.account_id
                    account_data["balance"] = lookup_account.balance
                    account_data["account_number"] = lookup_account.account_number
                    account_data["account_type"] = lookup_account.account_type
                    account_data["owner"] = lookup_account.owner
                else:
                    # not authorized
                    account_data = None

                return account_data

            def account_add(self, decrypted_auth_token, data):
                requesting_user_id = decrypted_auth_token["user_id"]
                requesters_account = Accounts.objects.filter(pk=requesting_user_id).first()

                if len(requesters_account):
                    requesters_type_id = requesters_account.account_type
                    requesters_type = requesters_account.account_type_name
                else:
                    return False  # TODO: handle this, raise an exception or something

                if len(data) and requesters_type == "bank_manager":
                    # bank manager requesting addition, so it's authorized
                    # TODO: NEED TO CHANGE THE REQUESTER TYPE CHECK -> do data sanitation and check for different cases/spacing between

                    # TODO: data sanitation for account addition
                    new_account = Accounts(account_id=data.account,
                                           balance=data.balance,
                                           account_number=data.account_number,
                                           account_type=data.account_type,
                                           owner=data.owner
                                           )
                    new_account.save()
                else:
                    return False;
                return True;