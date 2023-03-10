# Generated by Django 4.1.5 on 2023-01-12 01:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0002_bill_notes_alter_bill_bill_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bill',
            old_name='notes',
            new_name='note',
        ),
        migrations.RenameField(
            model_name='bill',
            old_name='provider_id',
            new_name='provider',
        ),
        migrations.AlterField(
            model_name='bill',
            name='due_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='bill',
            name='emission_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
