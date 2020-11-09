from django.db import models

# Create your models here.


class ATM(models.Model):
    """ATM Model"""
    class Meta:
        db_table = 'atm'
    state = models.CharField(verbose_name='state', max_length=255)
    street_address = models.CharField(
        verbose_name='street address', max_length=255, default='', blank=True)

    def __str__(self):
        return self.state + ',' + self.street_address
