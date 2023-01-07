from django.db import models

from hashid_field import HashidAutoField

class Provider(models.Model):
    id = HashidAutoField(primary_key=True)
    rif = models.CharField(max_length=15)
    name = models.CharField(max_length=70)
    nickname = models.CharField(max_length= 70)
    TAXES = [
        ('0','0% tax retained'),
        ('75','75% tax retained'),
        ('100','100% tax retained'),    
    ]
    taxtype = models.CharField(max_length=3, choices=TAXES)
    dollar_debt = models.FloatField(default=0)

    