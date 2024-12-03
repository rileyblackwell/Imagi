from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.Auth.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile for existing users that don\'t have one'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            self.stdout.write(f'Created profile for user: {user.username}') 