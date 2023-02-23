from django.db import models
import django

from hashid_field import HashidAutoField

from bills.models import Bill
from accounts.models import Account

default_account = Account.objects.get(pk='qDEzD98')
class Payment(models.Model):
    id = HashidAutoField(primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=False)
    date = models.DateField(default= django.utils.timezone.now)
    amount_bs = models.FloatField(default=0)
    amount_dollar = models.FloatField(default=0)
    exchange_rate = models.FloatField(default=0)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    paid_total = models.BooleanField(default=False)
    description = models.CharField(max_length=200, default='')
    transfer_id = models.CharField(max_length=50, default='')
    total_dollar = models.FloatField(default=0)
