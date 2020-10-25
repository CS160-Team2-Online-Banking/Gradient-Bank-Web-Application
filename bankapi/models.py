# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accounts(models.Model):
    using = 'bank_data'
    account_id = models.AutoField(primary_key=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2)
    account_number = models.IntegerField(unique=True)
    owner_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Accounts'


class BankManager(models.Model):
    using = 'online_banking_playground_1'
    bank_manager_id = models.AutoField(primary_key=True)
    hashed_pass = models.CharField(max_length=100)
    manager_email = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'Bank_Manager'


class Customer(models.Model):
    using = 'bank_data'
    customer_id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField(blank=True, null=True)
    autopayment_id = models.IntegerField(blank=True, null=True)
    customer_name = models.CharField(max_length=50)
    customer_phone = models.IntegerField()
    customer_email = models.CharField(max_length=50)
    customer_ssn = models.IntegerField(db_column='customer_SSN')  # Field name made lowercase.
    customer_address = models.CharField(max_length=50)
    customer_routingnumber = models.IntegerField(db_column='customer_routingNumber')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Customer'


class AutopaymentObjects(models.Model):
    using = 'bank_data'
    owner_user_id = models.IntegerField(primary_key=True)
    autopayment_id = models.IntegerField()
    payment_schedule_id = models.IntegerField()
    from_account_id = models.IntegerField()
    to_account_id = models.IntegerField()
    transfer_amount = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'autopayment_objects'
        unique_together = (('owner_user_id', 'autopayment_id'),)



class CompletedTransactionsLog(models.Model):
    using = 'bank_data'
    transaction_id = models.IntegerField(primary_key=True)
    started = models.DateTimeField()
    completed = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'completed_transactions_log'


class CompletedTransfersLog(models.Model):
    using = 'bank_data'
    transfer_id = models.IntegerField(primary_key=True)
    completed = models.DateTimeField()
    started = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'completed_transfers_log'

class EventLog(models.Model):
    using = 'bank_data'
    event_id = models.AutoField(primary_key=True)
    intiator_user_id = models.IntegerField()
    ip6_address = models.CharField(max_length=16, blank=True, null=True)
    ip4_address = models.CharField(max_length=4, blank=True, null=True)
    event_type = models.IntegerField()
    event_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'event_log'


class EventTypes(models.Model):
    using = 'bank_data'
    event_type_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    descrp = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event_types'


class PaymentSchedules(models.Model):
    using = 'bank_data'
    schedule_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_frequency = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = 'payment_schedules'


class PendingTransactionsQueue(models.Model):
    using = 'bank_data'
    transaction_id = models.IntegerField(primary_key=True)
    added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_transactions_queue'


class PendingTransfersQueue(models.Model):
    using = 'bank_data'
    transfer_id = models.IntegerField(primary_key=True)
    added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_transfers_queue'


class Transactions(models.Model):
    using = 'bank_data'
    transaction_id = models.AutoField(primary_key=True)
    card_account_id = models.IntegerField()
    merchant_id = models.IntegerField()
    card_network_id = models.IntegerField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    time_stamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'transactions'


class Transfers(models.Model):
    using = 'bank_data'
    transfer_id = models.AutoField(primary_key=True)
    create_event_id = models.IntegerField()
    to_account_id = models.IntegerField()
    from_account_id = models.IntegerField()
    transfer_type = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    time_stamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'transfers'
