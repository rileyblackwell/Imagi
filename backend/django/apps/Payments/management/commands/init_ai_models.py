from django.core.management.base import BaseCommand
from apps.Payments.models import AIModel

class Command(BaseCommand):
    help = 'Initialize AI models and their costs'

    def handle(self, *args, **kwargs):
        default_models = [
            {
                'name': 'Claude-3-Sonnet',
                'cost_per_use': 0.0400,
                'description': 'Anthropic\'s Claude 3 Sonnet - Advanced language model for complex tasks'
            },
            {
                'name': 'GPT-4',
                'cost_per_use': 0.0400,
                'description': 'OpenAI\'s GPT-4 - State-of-the-art language model for diverse applications'
            },
            {
                'name': 'GPT-4-Mini',
                'cost_per_use': 0.0020,
                'description': 'Optimized version of GPT-4 for faster, more cost-effective processing'
            }
        ]

        for model_data in default_models:
            model, created = AIModel.objects.update_or_create(
                name=model_data['name'],
                defaults={
                    'cost_per_use': model_data['cost_per_use'],
                    'description': model_data['description'],
                    'is_active': True
                }
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'{action} AI model: {model.name} (${model.cost_per_use:.4f} per use)')
            ) 