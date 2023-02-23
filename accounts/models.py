from django.db import models

from hashid_field import HashidAutoField


class Account(models.Model):
    id = HashidAutoField(primary_key=True)
    name = models.CharField(max_length=50,default='')
    description = models.CharField(max_length=100,default='')
    created_at = models.DateField(auto_now_add=True)