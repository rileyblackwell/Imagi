# Generated by Django 5.1.6 on 2025-03-15 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
