# Generated by Django 5.1.3 on 2024-12-03 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0002_rename_timestamp_payment_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='credits',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
