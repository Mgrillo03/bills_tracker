# Generated by Django 4.1.5 on 2023-01-21 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0006_rename_payed_bill_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='rest_to_pay_dollar',
            field=models.FloatField(default=0),
        ),
    ]
