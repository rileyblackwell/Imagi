"""
Move metering from tokens to dollars, and retire the prepaid-credit balance.

UsageEvent gains cost_usd, which rolling-window plan allowances are now summed
over. CreditBalance becomes StripeCustomer: the spendable balance is gone, so
all the row still does is hold the Stripe customer id. This is written as a
RenameModel + RemoveField rather than the delete-and-create Django's
autodetector infers, so existing stripe_customer_id values survive — losing
them would orphan every live subscription from its webhook.

Existing UsageEvent rows keep cost_usd = 0. They were recorded when runs were
metered by token count, and back-pricing them would retroactively spend an
allowance their owners were never told about. Both windows are at most 7 days
long, so the gap ages out on its own.
"""

from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Payments', '0003_alter_subscription_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='usageevent',
            name='cost_usd',
            field=models.DecimalField(
                decimal_places=6, default=Decimal('0'), max_digits=12
            ),
        ),
        migrations.RenameModel(
            old_name='CreditBalance',
            new_name='StripeCustomer',
        ),
        migrations.AlterModelOptions(
            name='stripecustomer',
            options={
                'verbose_name': 'Stripe Customer',
                'verbose_name_plural': 'Stripe Customers',
            },
        ),
        migrations.AlterField(
            model_name='stripecustomer',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='stripe_customer',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveField(
            model_name='stripecustomer',
            name='balance',
        ),
        # Dead since long before this change: nothing read or wrote these.
        migrations.RemoveField(model_name='aimodelusage', name='model'),
        migrations.RemoveField(model_name='aimodelusage', name='user'),
        migrations.DeleteModel(name='AIModelUsage'),
        migrations.DeleteModel(name='AIModel'),
        migrations.DeleteModel(name='CreditPlan'),
    ]
