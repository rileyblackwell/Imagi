from django.db import migrations


def forwards(apps, schema_editor):
    # The $200 tier is now Max (10x); rewrite rows stored under the old id.
    Subscription = apps.get_model('Payments', 'Subscription')
    Subscription.objects.filter(plan='max_20x').update(plan='max_10x')


def backwards(apps, schema_editor):
    Subscription = apps.get_model('Payments', 'Subscription')
    Subscription.objects.filter(plan='max_10x').update(plan='max_20x')


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0004_meter_usage_in_dollars'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
