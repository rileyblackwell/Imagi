from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('Payments', '0003_alter_payment_credits'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='credits',
        ),
    ] 