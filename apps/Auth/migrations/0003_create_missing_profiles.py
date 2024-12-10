from django.db import migrations

def create_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('Auth', 'Profile')
    
    for user in User.objects.all():
        Profile.objects.get_or_create(
            user=user,
            defaults={'credits': 0.00}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0002_create_profile_model'),
    ]

    operations = [
        migrations.RunPython(create_profiles),
    ] 