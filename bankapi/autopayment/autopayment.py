from bankapi.models import *
from django.db import transaction
from datetime import datetime
from django.core import serializers
import json


# In retrospect, this should have been named Autopayment Manager
class AutopaymentBuilder:

    @staticmethod
    @transaction.atomic(using="bank_data")
    def build_autopayment(decrypted_auth_token, payment_data):
        owner_id = decrypted_auth_token["user_id"]
        payment_schedule_data = payment_data["payment_schedule_data"]
        from_account_no = payment_data["from_account_no"]
        from_routing_no = payment_data["from_routing_no"]
        to_account_no = payment_data["to_account_no"]
        to_routing_no = payment_data["to_routing_no"]
        transfer_amount = payment_data["transfer_amount"]

        owner = Customer.objects.filter(pk=owner_id).first()
        if owner is None:
            return None  # TODO: handle this, raise an exception or something

        from_account = Accounts.objects.filter(account_number=from_account_no).first()

        if from_account is None:
            return None  # TODO: handle this, raise an exception or something

        # if all accounts associated with this account exist, and the user is authorized to setup transfers
        if from_account.owner_id == owner.pk:
            payment_frequency = payment_schedule_data["payment_frequency"]
            start_date = payment_schedule_data["start_date"]
            end_date = payment_schedule_data["end_date"]
            if transfer_amount < 0:
                return None
            if not PaymentFrequencies.validate_string(payment_frequency):
                return None  # TODO: handle this, raise an exception or something

            payment_schedule = PaymentSchedules(start_date=start_date,
                                                end_date=end_date,
                                                payment_frequency=payment_frequency)
            payment_schedule.save()

            other_payments = AutopaymentObjects.objects.filter(owner_user_id=owner.pk)
            all_payments = AutopaymentObjects.objects.all()
            new_id = 0 if not len(all_payments) else (all_payments.latest("id").id + 1)
            new_auto_payment_id = 0 if not len(other_payments) else (other_payments
                                                                     .latest('autopayment_id')
                                                                     .autopayment_id
                                                                     + 1)
            autopayment = AutopaymentObjects(owner_user_id=owner.pk,
                                             autopayment_id=new_auto_payment_id,
                                             payment_schedule_id=payment_schedule.pk,
                                             from_account_id=from_account.pk,
                                             to_account_no=to_account_no,
                                             to_routing_no=to_routing_no,
                                             transfer_amount=transfer_amount,
                                             id=new_id)
            autopayment.save()
            return autopayment.owner_user_id, autopayment.autopayment_id
        return None

    @staticmethod
    @transaction.atomic(using="bank_data")
    def modify_autopayment(decrypted_auth_token, payment_data):
        owner_id = decrypted_auth_token["user_id"]
        payment_id = payment_data["autopayment_id"]

        owner = Customer.objects.filter(pk=owner_id).first()
        if owner is None:
            return None

        autopay_obj = AutopaymentObjects.objects.filter(owner_user_id=owner.pk, autopayment_id=payment_id).first()
        if autopay_obj is None:
            return None

        if "from_account_no" in payment_data:
            new_from_account_no = payment_data["from_account_no"]
            new_f_account = Accounts.objects.filter(account_number=new_from_account_no).first()
            if new_f_account is None:
                return None
            if new_f_account.owner_id == owner_id:
                autopay_obj.from_account_id = new_f_account.pk
            else:
                return None

        if "to_account_no" in payment_data:
            autopay_obj.to_account_no = payment_data["to_account_no"]
        if "to_routing_no" in payment_data:
            autopay_obj.to_routing_no = payment_data["to_routing_no"]
        if "transfer_amount" in payment_data:
            transfer_amount = payment_data["transfer_amount"]
            if transfer_amount < 0:
                autopay_obj.transfer_amount = transfer_amount

        if "payment_schedule_data" in payment_data:
            schedule_data = payment_data["payment_schedule_data"]
            schedule_obj = autopay_obj.payment_schedule
            if "start_date" in schedule_data:
                schedule_obj.start_date = schedule_data["start_date"]
            if "end_date" in schedule_data:
                schedule_obj.start_date = schedule_data["end_date"]
            if "payment_frequency" in schedule_data:
                payment_freq = schedule_data["payment_frequency"]
                if not PaymentFrequencies.validate_string(payment_freq):
                    return None
                schedule_obj.payment_frequency = payment_freq
            schedule_obj.save()
        autopay_obj.save()

        return autopay_obj.owner_user_id, autopay_obj.autopayment_id

    @staticmethod
    def cancel_autopayment(decrypted_auth_token, autopayment_id):
        owner_id = decrypted_auth_token["user_id"]
        payment_id = autopayment_id
        print('<<<<<<<<<<<<<<<<<')
        print("i'm in bankapi autopayment deleteion")
        print("payment_id: ", payment_id)
        print("owner_id: ", owner_id)
        print('<<<<<<<<<<<<<<<<<')

        owner = Customer.objects.filter(pk=owner_id).first()
        if owner is None:
            return None

        autopay_obj = AutopaymentObjects.objects.filter(owner_user_id=owner.pk, autopayment_id=payment_id).first()
        if autopay_obj is None:
            return None
        autopay_obj.delete()
        return True  # TODO: return something nicer here

    @staticmethod
    def get_autopayment(decrypted_auth_token, autopayment_id):
        owner_id = decrypted_auth_token["user_id"]
        payment_id = autopayment_id

        owner = Customer.objects.filter(pk=owner_id).first()
        if owner is None:
            return None

        if autopayment_id is None:
            autopay_obj = AutopaymentObjects.objects.filter(owner_user_id=owner.pk)
        else:
            autopay_obj = AutopaymentObjects.objects.filter(owner_user_id=owner.pk, autopayment_id=payment_id)

        if autopay_obj.first() is None:
            return None
        json_arr = json.loads(serializers.serialize("json", autopay_obj))
        json_arr = list(map(lambda x: x["fields"], json_arr))

        for i, entry in enumerate(json_arr):
            payment_schedule_id = entry["payment_schedule"]
            payment_schedule = PaymentSchedules.objects.filter(pk=payment_schedule_id)
            entry["payment_schedule"] = json.loads(serializers.serialize("json", payment_schedule))[0]["fields"]
            entry["to_account_no"] = str(entry["to_account_no"]).zfill(12)
            entry["to_routing_no"] = str(entry["to_routing_no"]).zfill(9)
        return json_arr


def is_payment_due(autopayment_obj) -> bool:
    # if the current date is less than the end date and after the start date
    payment_schedule = autopayment_obj.payment_schedule
    start_datetime = datetime.combine(payment_schedule.start_date, datetime.min.time())
    end_datetime = datetime.combine(payment_schedule.end_date, datetime.min.time())
    now_time = datetime.now()
    if start_datetime < now_time < end_datetime:
        if autopayment_obj.last_payment is None:  # if no payment has been made yet
            return True

        last_payment_date = autopayment_obj.last_payment

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
