from django.db import migrations


def forwards(apps, schema_editor):
    # Every existing account starts on the Free plan and its weekly allowance,
    # in every environment this migration runs in. Accounts with no
    # Subscription row are already on Free (that is the default); this moves
    # any stored paid plan back to Free too. A real Stripe subscription would
    # set its plan again on the next subscription webhook event.
    Subscription = apps.get_model('Payments', 'Subscription')
    Subscription.objects.exclude(plan='free').update(plan='free')


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0005_rename_max_20x_to_max_10x'),
    ]

    operations = [
        # Not reversible in any meaningful way: which plan each row held is
        # not kept. Reversing is a no-op so the schema can still roll back.
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
