from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sell', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='billing_interval',
            field=models.CharField(
                choices=[
                    ('one_time', 'One-time purchase'),
                    ('month', 'Monthly subscription'),
                    ('year', 'Yearly subscription'),
                ],
                default='one_time',
                max_length=10,
            ),
        ),
    ]
