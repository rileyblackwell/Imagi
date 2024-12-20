from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration merges the rename credits to balance migration
    with the create missing profiles migration.
    """

    dependencies = [
        ('Auth', '0002_rename_credits_to_balance'),
        ('Auth', '0003_create_missing_profiles'),
    ]

    operations = [
        # No operations needed as this is just a merge migration
    ] 