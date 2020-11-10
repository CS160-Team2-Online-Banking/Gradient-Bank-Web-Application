# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accounts(models.Model):
    account_id = models.AutoField(primary_key=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2)
    account_number = models.IntegerField(unique=True)
    owner_id = models.IntegerField()
    account_type_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Accounts'


class BankManager(models.Model):
    bank_manager_id = models.AutoField(primary_key=True)
    hashed_pass = models.CharField(max_length=100)
    manager_email = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'Bank_Manager'


class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField(blank=True, null=True)
    autopayment_id = models.IntegerField(blank=True, null=True)
    customer_name = models.CharField(max_length=50)
    customer_phone = models.IntegerField()
    customer_email = models.CharField(max_length=50)
    # Field name made lowercase.
    customer_ssn = models.IntegerField(db_column='customer_SSN')
    customer_address = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Customer'


class AccountTypes(models.Model):
    account_type_id = models.IntegerField(primary_key=True)
    account_type_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'account_types'


class AutopaymentObjects(models.Model):
    id = models.IntegerField()
    owner_user_id = models.IntegerField(primary_key=True)
    autopayment_id = models.IntegerField()
    from_account_id = models.IntegerField()
    payment_schedule_id = models.IntegerField()
    to_account_no = models.BigIntegerField()
    to_routing_no = models.IntegerField()
    transfer_amount = models.DecimalField(max_digits=18, decimal_places=2)
    last_payment = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'autopayment_objects'
        unique_together = (('owner_user_id', 'autopayment_id'),)


class CompletedTransactionsLog(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    started = models.DateTimeField()
    completed = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'completed_transactions_log'


class CompletedTransfersLog(models.Model):
    transfer_id = models.IntegerField(primary_key=True)
    completed = models.DateTimeField()
    started = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'completed_transfers_log'


class DebitHistory(models.Model):
    from_account_no = models.BigIntegerField()
    from_routing_no = models.IntegerField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    time_started = models.DateTimeField()
    time_processed = models.DateTimeField(blank=True, null=True)
    debit_initator = models.ForeignKey(Customer, models.DO_NOTHING)
    to_account = models.ForeignKey(Accounts, models.DO_NOTHING)
    status = models.CharField(max_length=32, blank=True, null=True)
    pending = models.ForeignKey(
        'ExternalTransferPool', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'debit_history'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class EventLog(models.Model):
    event_id = models.AutoField(primary_key=True)
    intiator_user_id = models.IntegerField()
    ip6_address = models.CharField(max_length=16, blank=True, null=True)
    ip4_address = models.CharField(max_length=4, blank=True, null=True)
    event_type = models.IntegerField()
    event_time = models.DateTimeField()
    data_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event_log'


class EventTypes(models.Model):
    event_type_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    descrp = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event_types'


class ExchangeHistory(models.Model):
    to_account_no = models.BigIntegerField(blank=True, null=True)
    to_routing_no = models.IntegerField(blank=True, null=True)
    from_account_no = models.BigIntegerField()
    from_routing_no = models.IntegerField()
    atm_id = models.BigIntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    posted = models.DateTimeField()
    finished = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=16)
    status = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'exchange_history'


class ExternalAccounts(models.Model):
    external_account_id = models.AutoField(primary_key=True)
    routing_number = models.IntegerField()
    account_number = models.BigIntegerField()
    owner_user = models.ForeignKey(Customer, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'external_accounts'


class ExternalTransferPool(models.Model):
    pending_extern_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    inbound = models.IntegerField()
    internal_account = models.ForeignKey(Accounts, models.DO_NOTHING)
    debit_transfer = models.IntegerField()
    external_account_no = models.BigIntegerField()
    external_account_routing_no = models.IntegerField()
    exchange_obj = models.ForeignKey(
        ExchangeHistory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_transfer_pool'


class FailedTransactionsLog(models.Model):
    transaction = models.OneToOneField(
        'Transactions', models.DO_NOTHING, primary_key=True)
    started = models.DateTimeField()
    failed = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'failed_transactions_log'


class FailedTransfersLog(models.Model):
    transfer = models.OneToOneField(
        'Transfers', models.DO_NOTHING, primary_key=True)
    started = models.DateTimeField()
    failed = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'failed_transfers_log'


class PaymentNetworks(models.Model):
    network_id = models.IntegerField(primary_key=True)
    # Field name made lowercase.
    network_gid = models.IntegerField(
        db_column='network_GID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_networks'


class PaymentSchedules(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_frequency = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = 'payment_schedules'


class PendingTransactionsQueue(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_transactions_queue'


class PendingTransfersQueue(models.Model):
    transfer_id = models.IntegerField(primary_key=True)
    added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_transfers_queue'


class Transactions(models.Model):
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


class FailedTransfers(models.Model):
    use_db = 'bank_data'
    transfer = models.OneToOneField(Transfers, related_name="f_trnsfr_to_trnsfr", primary_key=True,
                                    db_column="transfer_id", on_delete=models.CASCADE)
    started = models.DateTimeField()
    failed = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'failed_transfers_log'

class TransferTypes:
    U_TO_U = 'U_TO_U'
    A_TO_A = 'A_TO_A'
    EXTERN = 'EXTERN'


TRANSFER_QUEUE_EVENT_ID = EventTypes.objects.get(name="TRANSFER QUEUED").pk
TRANSFER_CANCEL_EVENT_ID = EventTypes.objects.get(name="TRANSFER CANCELED").pk
DEBIT_QUEUED_EVENT_ID = EventTypes.objects.get(name="DEBIT QUEUED").pk
SAVING_ACCOUNT_ID = 1
if AccountTypes.objects.filter(pk=SAVING_ACCOUNT_ID).first() is None:
    saving = AccountTypes(account_type_id=SAVING_ACCOUNT_ID,
                          account_type_name='SAVING')
    saving.save()
CHECKING_ACCOUNT_ID = 2
if AccountTypes.objects.filter(pk=CHECKING_ACCOUNT_ID).first() is None:
    checking = AccountTypes(
        account_type_id=CHECKING_ACCOUNT_ID, account_type_name='CHECKING')
    checking.save()
