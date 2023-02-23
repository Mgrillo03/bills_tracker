from django.db import models
import django

from hashid_field import HashidAutoField

from providers.models import Provider


class Bill(models.Model):
    """
        Bill class
        the bill can be in 2 currencies at the same time (bolivar and dollar)
        the taxes are calculated in both currencies separately and unified at the end
        so the total amount in the bill is always calculated in dollar
    """
    id = HashidAutoField(primary_key=True)
    bill_number = models.CharField(max_length=20,null=False) #original bill number
    emission_date = models.DateField(default= django.utils.timezone.now) 
    due_date = models.DateField(default= django.utils.timezone.now)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=False)

    amount_bs = models.FloatField(default=0) # total amount billed in bolivares
    sub_total_bs = models.FloatField(default=0) # total amount - taxes
    tax_bs = models.FloatField(default=0) #  taxes (16%)
    retained_tax_bs = models.FloatField(default=0) # part of taxes that will not be paid
    amount_to_pay_bs = models.FloatField(default=0) # total amount to pay from the bolivares billed part

    exchange_rate = models.FloatField(default=0) # exchange rate from bolivares to dollar

    amount_dollar = models.FloatField(default=0) # total amount billed in dollar
    sub_total_dollar = models.FloatField(default=0) # total - taxes
    tax_dollar = models.FloatField(default=0) # taxes (16%)
    retained_tax_dollar = models.FloatField(default=0) # part of taxes that will not be paid
    amount_to_pay_dollar = models.FloatField(default=0) # total amount to pay fromm the dollars billed part

    bill_total_dollar = models.FloatField(default=0) # real total amount billed, adding up total in bolivares and total in dollar
    total_to_pay_dollar = models.FloatField(default=0) # total amount to pay, adding up both parts
    amount_paid_dollar = models.FloatField(default=0) # amount already paid 
    rest_to_pay_dollar = models.FloatField(default=0) # amount that rest to pay from the bill

    paid = models.BooleanField(default='False') # True: completely paid- False: not completely paid
    note = models.CharField(max_length=200, default='') # some payment description
    overdue = models.FloatField(default=False) # indicades if the due date already passed
