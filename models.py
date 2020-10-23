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
    customer_ssn = models.IntegerField(db_column='customer_SSN')  # Field name made lowercase.
    customer_address = models.CharField(max_length=50)
    customer_routingnumber = models.IntegerField(db_column='customer_routingNumber')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Customer'


class AccountEmailaddress(models.Model):
    email = models.CharField(unique=True, max_length=254)
    verified = models.IntegerField()
    primary = models.IntegerField()
    user = models.ForeignKey('AccountsCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailaddress'


class AccountEmailconfirmation(models.Model):
    created = models.DateTimeField()
    sent = models.DateTimeField(blank=True, null=True)
    key = models.CharField(unique=True, max_length=64)
    email_address = models.ForeignKey(AccountEmailaddress, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailconfirmation'


class AccountsCustomuser(models.Model):
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    password = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    sex = models.IntegerField(blank=True, null=True)
    admin = models.IntegerField(blank=True, null=True)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'accounts_customuser'


class AccountsCustomuserGroups(models.Model):
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_customuser_groups'
        unique_together = (('customuser', 'group'),)


class AccountsCustomuserUserPermissions(models.Model):
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AutopaymentObjects(models.Model):
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


class BankAccounts(models.Model):
    account_id = models.IntegerField(primary_key=True)
    owner_id = models.IntegerField()
    balance = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'bank_accounts'


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


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class EventLog(models.Model):
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
    event_type_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=32)
    descrp = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event_types'


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


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=30)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.TextField()
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)


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
