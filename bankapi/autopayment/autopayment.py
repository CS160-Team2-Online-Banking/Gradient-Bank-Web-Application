from bankapi.models import *
from django.db import transaction
from datetime import datetime
from bankapi.utils.network_utils import get_datetime_from_str
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

def is_payment_due(autopayment_obj) -> bool:
    # if the current date is less than the end date and after the start date
    payment_schedule = autopayment_obj.payment_schedule
    start_datetime = get_datetime_from_str(payment_schedule.start_date)
    end_datetime = get_datetime_from_str(payment_schedule.end_date)
    now_time = datetime.now()

    if start_datetime < now_time < end_datetime:
        if autopayment_obj.last_payment is None:  # if no payment has been made yet
            return True

        last_payment_date = get_datetime_from_str(autopayment_obj.last_payment)

        if payment_schedule.payment_frequency == PaymentFrequencies.DAILY:
            return now_time.day > last_payment_date.day
        elif payment_schedule.payment_frequency == PaymentFrequencies.WEEKLY:
            #  isocalendar returns a tuple with the year[0], week number[1], and day number[2]
            return now_time.isocalendar()[1] > last_payment_date.isocalendar()[1]
        elif payment_schedule.payment_frequency == PaymentFrequencies.MONTHLY:
            return now_time.month > last_payment_date.month
        elif payment_schedule.payment_frequency == PaymentFrequencies.YEARLY:
            return now_time.year > last_payment_date.year
    return False
