from django.db import models
import django

from hashid_field import HashidAutoField

from providers.models import Provider


class Bill(models.Model):
    id = HashidAutoField(primary_key=True)
    bill_number = models.CharField(max_length=20,null=False)
    emission_date = models.DateField(default= django.utils.timezone.now)
    due_date = models.DateField(default= django.utils.timezone.now)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=False)
    total_amount_bs = models.FloatField(default=0)
    sub_total_bs = models.FloatField(default=0)
    tax_bs = models.FloatField(default=0)
    retained_tax_bs = models.FloatField(default=0)
    amount_to_pay_bs = models.FloatField(default=0)
    exchange_rate = models.FloatField(default=0)
    total_amount_dollar = models.FloatField(default=0)
    amount_to_pay_dollar = models.FloatField(default=0)
    paid = models.BooleanField(default='False')
    note = models.CharField(max_length=200, default='')
    rest_to_pay_dollar = models.FloatField(default=0)