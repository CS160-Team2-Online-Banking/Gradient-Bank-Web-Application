from django.db import models

class SampleDB(models.Model):
    class Meta:
        db_table = 'sample_table' # table name used in Database
        verbose_name_plural = 'sample_table' # table name that is displayed on Admin page
    sample1 = models.IntegerField('sample1', null=True, blank=True) # Integer
    sample2 = models.CharField('sample2', max_length=255, null=True, blank=True) # string
