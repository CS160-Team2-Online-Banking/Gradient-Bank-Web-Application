from bankapi.models import *
from django.db import transaction
import re


class AutopaymentBuilder:

    @staticmethod
    @transaction.atomic
    def build_autopayment(decrypted_auth_token, payment_data):
        owner_id = decrypted_auth_token["user_id"]
        payment_schedule_data = payment_data["payment_schedule_data"]
        from_account_id = payment_data["from_account_id"]
        to_account_id = payment_data["to_account_id"]
        transfer_amount = payment_data["transfer_amount"]
        transfer_type = payment_data["transfer_type"]

        owner = Customer.objects.filter(pk=owner_id).first()
        if owner is None:
            return None  # TODO: handle this, raise an exception or something

        from_account = Accounts.objects.filter(pk=from_account_id).first()
        if from_account is None:
            return None  # TODO: handle this, raise an exception or something

        if transfer_type == TransferTypes.EXTERN:
            to_account = ExternalAccount.objects.filter(pk=to_account_id).first()
        else:
            to_account = Accounts.objects.filter(pk=to_account_id).first()
            transfer_type = TransferTypes.U_TO_U
        if to_account is None:
            return None  # TODO: handle this, raise an exception or something


        # if all accounts associated with this account exist, and the user is authorized to setup transfers
        if from_account.owner_user_id == owner.pk:
            payment_frequency = payment_schedule_data["payment_frequency"]
            start_date = payment_schedule_data["start_date"]
            end_date = payment_schedule_data["end_date"]

            if not PaymentFrequencies.validate_string(payment_frequency):
                return None  # TODO: handle this, raise an exception or something

            payment_schedule = PaymentSchedules(start_date=start_date,
                                                end_date=end_date,
                                                payment_frequency=payment_frequency)
            payment_schedule.save()
            new_auto_payment_id = (AutopaymentObjects
                                   .objects
                                   .filter(owner_user_id=owner.pk)
                                   .latest('autopayment_id')
                                   .autopayment_id
                                   + 1)
            autopayment = AutopaymentObjects(owner_user_id=owner.pk,
                                             autopayment_id=new_auto_payment_id,
                                             payment_schedule=payment_schedule.pk,
                                             from_account=from_account.pk,
                                             to_account=to_account.pk,
                                             transfer_amount=transfer_amount,
                                             transfer_type=transfer_type)
            autopayment.save()
        return (owner.pk, autopayment.pk)

