from django.db import models
from django.db.transaction import atomic
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from bankapi.models import *

# Create your models here

# CustomUserManager


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, commit=True, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')

        # TODO: add methods to create/link a bank customer account from the 'bank_data' db
        # TODO: then save the data and set the primary key of that customer object to the bank_customer_id
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

    def create_user(self, email, password, commit=True, **extra_fields):
        # TODO: see above, i think you need to add extra_fields for all the stuff needed to create a bank customer
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, commit=True, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class UserTypes:
        TYPE_MANAGER = 2
        TYPE_CUSTOMER = 1
    password = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(
        max_length=255, null=True, unique=True, blank=True)
    email = models.CharField(max_length=255, null=True,
                             unique=True, blank=True)
    admin = models.IntegerField(null=True, blank=True)

    # Flags for permission to access the admin site

    type = models.IntegerField(default=UserTypes.TYPE_CUSTOMER)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    # Flag of whether the user is in the main registration status, False is temporary registration.

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = CustomUserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    PASSWORD_FIELD = 'password'

    REQUIRED_FIELDS = [EMAIL_FIELD]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return str(self.username)


class CustomerManager(CustomUserManager):
    use_in_migrations = True

    #TODO: Check this
    @atomic
    def create_user(self, email, password, **extra_fields):
        # from extra fields, we need to extract the
        middle_initial = extra_fields.get("middle_initial", None)
        suffix = extra_fields.get("suffix", None)
        last_name = extra_fields["last_name"]
        if suffix:
            last_name += "@"+suffix
        if middle_initial is not None:
            middle_initial = "{middle_initial}$".format(middle_initial=middle_initial)
        else:
            middle_initial = ""
        customer_name = "{first_name}${middle_initial}{last_name}".format(first_name=extra_fields["first_name"],
                                                                          middle_initial=middle_initial,
                                                                          last_name=last_name)
        customer_phone = extra_fields["phone"]
        customer_ssn = extra_fields["ssn"]
        customer_address = extra_fields["address"]
        customer_zip = extra_fields["zip"]
        customer_city = extra_fields["city"]
        customer_state = extra_fields["state"]
        customer_pin = extra_fields["pin"]
        extra_fields.pop('ssn', None)
        extra_fields.pop('address', None)
        extra_fields.pop('first_name', None)
        extra_fields.pop('middle_initial', None)
        extra_fields.pop('last_name', None)
        extra_fields.pop('suffix', None)
        extra_fields.pop('phone', None)
        extra_fields.pop('zip', None)
        extra_fields.pop('city', None)
        extra_fields.pop('state', None)
        extra_fields.pop('pin', None)
        extra_fields.pop('password1', None)
        extra_fields.pop('password2', None)
        user = super().create_user(email, password, commit=False, **extra_fields)
        bank_customer = Customer(pk=user.pk,
                                 customer_name=customer_name,
                                 customer_phone=customer_phone,
                                 customer_email=user.email,
                                 customer_ssn=customer_ssn,
                                 customer_address=customer_address,
                                 customer_zip=customer_zip,
                                 customer_city=customer_city,
                                 customer_state=customer_state,
                                 customer_pin=customer_pin)
        bank_customer.save()
        user.bank_customer_id = bank_customer.pk
        user.save(using=self._db)
        return user

    @staticmethod
    def update_user_info(user, commit=True, **changes):
        bank_customer = Customer.objects.filter(pk=user.pk).first()
        if bank_customer is None:
            return bank_customer

        customer_ssn = changes.pop('ssn', None)
        if customer_ssn:
            bank_customer.customer_ssn = customer_ssn

        customer_address = changes.pop('address', None)
        if customer_address:
            bank_customer.customer_address = customer_address

        first_name = changes.pop('first_name', None)
        middle_initial = changes.pop('middle_initial', None)
        last_name = changes.pop('last_name', None)
        suffix = changes.pop('suffix', None)
        if suffix:
            last_name += "@"+suffix
        if first_name and last_name:
            if middle_initial:
                customer_name = "{first_name}${middle_initial}${last_name}".format(first_name=first_name,
                                                                                   middle_initial=middle_initial,
                                                                                   last_name=last_name)
            else:
                customer_name = "{first_name}${last_name}".format(first_name=first_name,
                                                                  last_name=last_name)
            bank_customer.customer_name = customer_name

        customer_phone = changes.pop('phone', None)
        if customer_phone:
            bank_customer.customer_phone = customer_phone

        customer_zip = changes.pop('zip', None)
        if customer_zip:
            bank_customer.customer_zip = customer_zip

        customer_city = changes.pop('city', None)
        if customer_city:
            bank_customer.customer_city = customer_city

        customer_email = changes.get('email', None)
        if customer_email:
            bank_customer.customer_email = customer_email

        customer_state = changes.pop('state', None)
        if customer_state:
            bank_customer.customer_state = customer_state

        customer_pin = changes.pop('pin', None)
        if customer_pin:
            bank_customer.customer_pin = customer_pin
        if commit:
            bank_customer.save()
        return bank_customer


class EmployeeManager(CustomUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.pop('password1', None)
        extra_fields.pop('password2', None)
        extra_fields["type"] = CustomerUser.UserTypes.TYPE_MANAGER
        user = super()._create_user(email, password, commit=False, **extra_fields)
        new_manager_id = self.latest('manager_id')
        if new_manager_id is None:
            new_manager_id = 1
        else:
            new_manager_id = new_manager_id.manager_id + 1
        user.manager_id = new_manager_id
        user.save(using=self._db)
        return user


# CustomerUser

class CustomerUser(CustomUser, PermissionsMixin):
    bank_customer_id = models.IntegerField()

    objects = CustomerManager()


class BankManagerUser(CustomUser, PermissionsMixin):
    manager_id = models.IntegerField()

    objects = EmployeeManager()
