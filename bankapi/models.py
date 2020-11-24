# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import re


class BankManager(models.Model):
    use_db = 'bank_data'
    bank_manager_id = models.AutoField(primary_key=True)
    hashed_pass = models.CharField(max_length=100)
    manager_email = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'Bank_Manager'


class Customer(models.Model):
    use_db = 'bank_data'
    customer_id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField(blank=True, null=True)
    autopayment_id = models.IntegerField(blank=True, null=True)
    customer_name = models.CharField(max_length=50)
    customer_phone = models.BigIntegerField()
    customer_email = models.CharField(max_length=50)
    # Field name made lowercase.
    customer_ssn = models.IntegerField(db_column='customer_SSN')
    customer_address = models.CharField(max_length=50)
    customer_zip = models.CharField(max_length=5, null=True)
    customer_city = models.CharField(max_length=45, null=True)
    customer_state = models.CharField(max_length=2, null=True)
    customer_pin = models.CharField(max_length=4, null=True)
    closed = models.BooleanField(default=False)
    class Meta:
        managed = False
        db_table = 'Customer'


class AccountTypes(models.Model):
    use_db = 'bank_data'
    account_type_id = models.IntegerField(primary_key=True)
    account_type_name = models.CharField(max_length=64)

    class Meta:
        managed = True
        db_table = 'account_types'


class Accounts(models.Model):
    use_db = 'bank_data'
    account_id = models.AutoField(primary_key=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2)
    account_number = models.BigIntegerField(unique=True)
    account_type = models.ForeignKey(AccountTypes, related_name="acct_to_actyp", db_column='account_type_id',
                                     on_delete=models.RESTRICT)
    owner = models.ForeignKey(Customer, related_name="acct_to_cstmr",
                              db_column="owner_id", on_delete=models.RESTRICT)

    class Meta:
        managed = False
        db_table = 'Accounts'


class ExternalAccount(models.Model):
    use_db = 'bank_data'
    external_account_id = models.AutoField(primary_key=True)
    owner_user = models.ForeignKey(Customer, related_name="exa_to_cstmr", db_column="owner_user_id",
                                   on_delete=models.RESTRICT)
    routing_number = models.IntegerField()
    account_number = models.BigIntegerField()

    class Meta:
        managed = True
        db_table = 'external_accounts'


"""
class EventTypes(models.Model):
    use_db = 'bank_data'
    event_type_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    descrp = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event_types'
"""


class EventLog(models.Model):
    use_db = 'bank_data'
    event_id = models.AutoField(primary_key=True)
    intiator_user = models.ForeignKey(Customer, related_name="evnt_to_custmr", db_column="intiator_user_id",
                                      on_delete=models.RESTRICT)
    ip6_address = models.BinaryField(max_length=16, blank=True, null=True)
    ip4_address = models.BinaryField(max_length=4, blank=True, null=True)
    # event_type = models.ForeignKey(EventTypes, related_name="event_type", db_column="event_type",
    #                               on_delete=models.RESTRICT)
    event_type = models.IntegerField()
    event_time = models.DateTimeField()
    data_id = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'event_log'


class EventTypes:
    CREATE_ACCOUNT = (0, "CREATE ACCOUNT", "")
    REQUEST_TRANSFER = (1, "REQUEST TRANSFER", "")
    SETUP_AUTOPAYMENT = (2, "SETUP AUTOPAYMENT", "")
    EDIT_AUTOPAYMENT = (3, "EDIT AUTOPAYMENT", "")
    CANCEL_AUTOPAYMENT = (4, "CANCEL AUTOPAYMENT", "")
    CLOSE_ACCOUNT = (5, "CLOSE ACCOUNT", "")
    DEPOSIT_CHECK = (6, "DEPOSIT CHECK", "")
    SUSPICIOUS_TRANSFER = (7, "SUS TRANSFER", "")
    WITHDRAW_MONEY = (8, "WITHDRAW", "")
    EVENT_ARR = [CREATE_ACCOUNT, REQUEST_TRANSFER, SETUP_AUTOPAYMENT, EDIT_AUTOPAYMENT, CANCEL_AUTOPAYMENT,
                 CLOSE_ACCOUNT, DEPOSIT_CHECK, SUSPICIOUS_TRANSFER, WITHDRAW_MONEY]


class PaymentSchedules(models.Model):
    use_db = 'bank_data'
    schedule_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_frequency = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = 'payment_schedules'


class PaymentFrequencies:
    YEARLY = 'YEARLY'
    MONTHLY = 'MONTHLY'
    WEEKLY = 'WEEKLY'
    DAILY = 'DAILY'
    REGEX = '({y})|({m})|({w})|({d})'.format(
        y=YEARLY, m=MONTHLY, w=WEEKLY, d=DAILY)

    @staticmethod
    def validate_string(str):
        result = re.findall(PaymentFrequencies.REGEX, str)
        return len(result) == 1


class AutopaymentObjects(models.Model):
    use_db = 'bank_data'
    id = models.IntegerField(primary_key=True)
    owner_user = models.ForeignKey(Customer, related_name="autop_to_custmr", db_column="owner_user_id",
                                   on_delete=models.RESTRICT)
    autopayment_id = models.IntegerField()
    payment_schedule = models.OneToOneField(PaymentSchedules, related_name="autop_pymnt_schedule",
                                            db_column="payment_schedule_id", on_delete=models.CASCADE)
    from_account = models.ForeignKey(Accounts, related_name="autop_from_to_acct", db_column="from_account_id",
                                     on_delete=models.RESTRICT)
    to_account_no = models.BigIntegerField()
    to_routing_no = models.IntegerField()
    transfer_amount = models.DecimalField(max_digits=18, decimal_places=2)
    last_payment = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = 'autopayment_objects'
        unique_together = (('owner_user_id', 'autopayment_id'),)


class PaymentNetworks(models.Model):
    use_db = 'bank_data'
    network_id = models.IntegerField(primary_key=True)
    network_GID = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'payment_networks'


class Transactions(models.Model):
    use_db = 'bank_data'
    transaction_id = models.AutoField(primary_key=True)
    card_account = models.ForeignKey(Accounts, related_name="trrnsct_from_to_acct", db_column="card_account_id",
                                     on_delete=models.RESTRICT)
    merchant_id = models.IntegerField()
    card_network = models.ForeignKey(PaymentNetworks, related_name="trnsct_to_ntwrk", db_column="card_network_id",
                                     on_delete=models.RESTRICT)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    time_stamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'transactions'


class Transfers(models.Model):
    use_db = 'bank_data'
    transfer_id = models.AutoField(primary_key=True)
    create_event = models.ForeignKey(EventLog, related_name="trnsfr_to_evnt", db_column="create_event_id",
                                     on_delete=models.RESTRICT)
    to_account_id = models.IntegerField()
    # to_account = models.ForeignKey(Accounts, related_name="trnsfr_from_to_acct", db_column="to_account_id", on_delete=models.RESTRICT)
    from_account = models.ForeignKey(Accounts, related_name="trnsfr_to_to_acct", db_column="from_account_id",
                                     on_delete=models.RESTRICT)
    transfer_type = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    time_stamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'transfers'


class ExchangeHistory(models.Model):
    use_db = 'bank_data'

    class ExchangeTypes:
        DEPOSIT = "DEPOSIT"
        TRANSFER = "TRANSFER"
        WITHDRAWAL = "WITHDRAWAL"

    class ExchangeHistoryStatus:
        FINISHED = "FINISHED"
        POSTED = "POSTED"
        FAILED = "FAILED"
        CANCELED = "CANCELED"
        FLAGGED = "FLAGGED"

    id = models.AutoField(primary_key=True)
    to_account_no = models.BigIntegerField(null=True)
    to_routing_no = models.IntegerField(null=True)
    from_account_no = models.BigIntegerField()
    from_routing_no = models.IntegerField()
    atm_id = models.BigIntegerField(null=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    posted = models.DateTimeField()
    finished = models.DateTimeField(null=True)
    type = models.CharField(max_length=16, default=ExchangeTypes.TRANSFER)
    status = models.CharField(
        max_length=16, default=ExchangeHistoryStatus.POSTED)

    class Meta:
        managed = True
        db_table = 'exchange_history'


class ExternalTransferPool(models.Model):
    use_db = 'bank_data'
    pending_extern_id = models.AutoField(primary_key=True)
    internal_account = models.ForeignKey(Accounts, related_name="etp_to_acc", db_column="internal_account_id",
                                         on_delete=models.RESTRICT)
    external_account_routing_no = models.IntegerField(default=0)
    external_account_no = models.BigIntegerField(default=0)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    # indicates whether money should be moved to the internal account
    inbound = models.BooleanField()
    # debit indicates it's a debit transfer (we're pulling money)
    debit_transfer = models.BooleanField(default=False)
    exchange_obj = models.ForeignKey(ExchangeHistory, related_name="etp_to_exch", db_column="exchange_obj_id",
                                     on_delete=models.RESTRICT, null=True)

    class Meta:
        managed = True
        db_table = 'external_transfer_pool'


class DebitHistory(models.Model):
    use_db = 'bank_data'
    id = models.AutoField(primary_key=True)
    debit_intiator = models.ForeignKey(
        Customer, related_name="dbt_to_cstmr", db_column="debit_initator_id", on_delete=models.RESTRICT)
    from_account_no = models.BigIntegerField()
    from_routing_no = models.IntegerField()
    to_account = models.ForeignKey(
        Accounts, related_name="dbt_to_acct", db_column="to_account_id", on_delete=models.RESTRICT)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    time_started = models.DateTimeField()
    time_processed = models.DateTimeField(null=True)
    pending_queue_obj = models.ForeignKey(ExternalTransferPool, related_name="dbt_to_extpo", db_column="pending_id",
                                          on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=32, null=True)

    class Meta:
        managed = True
        db_table = 'debit_history'


class TransferTypes:
    U_TO_U = 'U_TO_U'
    A_TO_A = 'A_TO_A'
    EXTERN = 'EXTERN'


class PendingTransactionsQueue(models.Model):
    use_db = 'bank_data'
    transaction = models.OneToOneField(Transactions, related_name="p_trnsct_to_trnsct", primary_key=True,
                                       db_column="transaction_id", on_delete=models.CASCADE)
    added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_transactions_queue'


class PendingTransfersQueue(models.Model):
    use_db = 'bank_data'
    transfer = models.OneToOneField(Transfers, related_name="p_trnsfr_to_trnsfr", primary_key=True,
                                    db_column="transfer_id", on_delete=models.CASCADE)
    added = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_transfers_queue'


class CompletedTransactionsLog(models.Model):
    use_db = 'bank_data'
    transaction = models.OneToOneField(Transactions, related_name="c_trnsct_to_trnsct", primary_key=True,
                                       db_column="transaction_id", on_delete=models.CASCADE)
    started = models.DateTimeField()
    completed = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'completed_transactions_log'


class CompletedTransfersLog(models.Model):
    use_db = 'bank_data'
    transfer = models.OneToOneField(Transfers, related_name="c_trnsfr_to_trnsfr", primary_key=True,
                                    db_column="transfer_id", on_delete=models.CASCADE)
    completed = models.DateTimeField()
    started = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'completed_transfers_log'


class FailedTransfers(models.Model):
    use_db = 'bank_data'
    transfer = models.OneToOneField(Transfers, related_name="f_trnsfr_to_trnsfr", primary_key=True,
                                    db_column="transfer_id", on_delete=models.CASCADE)
    started = models.DateTimeField()
    failed = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'failed_transfers_log'


class FailedTransactions(models.Model):
    use_db = 'bank_data'
    transaction = models.OneToOneField(Transactions, related_name="f_trnsct_to_trnsct", primary_key=True,
                                       db_column="transaction_id", on_delete=models.CASCADE)
    started = models.DateTimeField()
    failed = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'failed_transactions_log'


class SuspiciousExchange(models.Model):
    use_db = 'bank_data'
    exchange = models.OneToOneField(ExchangeHistory, related_name="s_susexch_to_exch", primary_key=True,
                                    db_column="exchange_id", on_delete=models.CASCADE)
    flag_date = models.DateTimeField()
    resolve_date = models.DateTimeField(null=True)
    reviewer = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'suspicious_exchanges'

        
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
