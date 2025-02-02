from django.core.management.base import BaseCommand
from apps.Payments.models import CreditPackage

class Command(BaseCommand):
    help = 'Initialize default credit packages'

    def handle(self, *args, **kwargs):
        default_packages = [
            {
                'id': 'starter',
                'name': 'Starter Package',
                'amount': 10.00,
                'credits': 100,
                'features': [
                    'Build simple web applications',
                    'Basic AI assistance',
                    '30-day validity'
                ],
                'is_popular': False
            },
            {
                'id': 'pro',
                'name': 'Pro Package',
                'amount': 25.00,
                'credits': 300,
                'features': [
                    'Build complex applications',
                    'Advanced AI features',
                    '60-day validity',
                    'Priority support'
                ],
                'is_popular': True
            },
            {
                'id': 'enterprise',
                'name': 'Enterprise Package',
                'amount': 50.00,
                'credits': 1000,
                'features': [
                    'Unlimited application complexity',
                    'Premium AI features',
                    '90-day validity',
                    '24/7 priority support',
                    'Custom solutions'
                ],
                'is_popular': False
            }
        ]

        for package_data in default_packages:
            CreditPackage.objects.update_or_create(
                id=package_data['id'],
                defaults={
                    'name': package_data['name'],
                    'amount': package_data['amount'],
                    'credits': package_data['credits'],
                    'features': package_data['features'],
                    'is_popular': package_data['is_popular'],
                    'is_active': True
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created/updated package: {package_data["name"]}')
            ) 