from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

# Create your models here

# CustomUserManager


class CustomUserManager(UserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')

        # TODO: add methods to create/link a bank customer account from the 'bank_data' db
        # TODO: then save the data and set the primary key of that customer object to the bank_customer_id
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        # TODO: see above, i think you need to add extra_fields for all the stuff needed to create a bank customer
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


# CustomerUser


class CustomUser(AbstractBaseUser, PermissionsMixin):
    password = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(
        max_length=255, null=True, unique=True, blank=True)
    email = models.CharField(max_length=255, null=True,
                             unique=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    sex = models.IntegerField(null=True, blank=True)
    admin = models.IntegerField(null=True, blank=True)
    bank_customer_id = models.IntegerField(null=True, blank=True)
    # Flags for permission to access the admin site

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
    REQUIRED_FIELDS = [EMAIL_FIELD]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return str(self.username)
