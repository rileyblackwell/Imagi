from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.Imagi.Marketing.models import AdConnection, MarketingSettings
from apps.Imagi.ProjectManager.models import Project
from apps.Imagi.Sell.models import SellSettings

OLD = 'old-secret-key-that-may-have-leaked'
NEW = 'new-secret-key-after-rotation'


class ReencryptSecretsTests(TestCase):
    """Rotating DJANGO_SECRET_KEY must not lose the credentials users saved:
    the old key keeps them readable until reencrypt_secrets moves them."""

    def setUp(self):
        user = User.objects.create_user(username='owner', password='pass12345')
        self.project = Project.objects.create(name='Bloom Coffee', user=user)
        with override_settings(SECRET_KEY=OLD, OLD_SECRET_KEY=''):
            self.sell = SellSettings(project=self.project)
            self.sell.stripe_secret_key = 'sk_test_owner'
            self.sell.stripe_webhook_secret = 'whsec_owner'
            self.server_key = self.sell.rotate_server_key()
            self.sell.save()
            self.marketing = MarketingSettings(project=self.project, twilio_account_sid='AC1')
            self.marketing.twilio_auth_token = 'twilio-token'
            self.marketing.save()
            self.ads = AdConnection(project=self.project, provider=AdConnection.PROVIDER_META)
            self.ads.credentials = {'access_token': 'meta-token'}
            self.ads.save()

    def _read(self):
        sell = SellSettings.objects.get(pk=self.sell.pk)
        return (
            sell.stripe_secret_key, sell.stripe_webhook_secret, sell.server_key,
            MarketingSettings.objects.get(pk=self.marketing.pk).twilio_auth_token,
            AdConnection.objects.get(pk=self.ads.pk).credentials,
        )

    def _expected(self):
        return ('sk_test_owner', 'whsec_owner', self.server_key, 'twilio-token',
                {'access_token': 'meta-token'})

    def test_a_new_key_alone_cannot_read_old_values(self):
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=''):
            self.assertEqual(self._read(), ('', '', '', '', {}))

    def test_old_key_keeps_values_readable_before_the_move(self):
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=OLD):
            self.assertEqual(self._read(), self._expected())

    def test_command_moves_every_value_to_the_new_key(self):
        out = StringIO()
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=OLD):
            call_command('reencrypt_secrets', stdout=out)
        self.assertIn('moved 5', out.getvalue())
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=''):
            self.assertEqual(self._read(), self._expected())

    def test_second_run_finds_nothing_to_move(self):
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=OLD):
            call_command('reencrypt_secrets', stdout=StringIO())
            out = StringIO()
            call_command('reencrypt_secrets', stdout=out)
        self.assertIn('moved 0', out.getvalue())

    def test_new_values_are_written_under_the_new_key(self):
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=OLD):
            sell = SellSettings.objects.get(pk=self.sell.pk)
            sell.stripe_secret_key = 'sk_test_fresh'
            sell.save()
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=''):
            self.assertEqual(SellSettings.objects.get(pk=self.sell.pk).stripe_secret_key, 'sk_test_fresh')

    def test_value_under_neither_key_is_counted_and_left_alone(self):
        with override_settings(SECRET_KEY='some-other-key', OLD_SECRET_KEY=''):
            m = MarketingSettings.objects.get(pk=self.marketing.pk)
            m.twilio_auth_token = 'orphan'
            m.save()
        stored = MarketingSettings.objects.get(pk=self.marketing.pk).twilio_auth_token_encrypted
        out = StringIO()
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=OLD):
            call_command('reencrypt_secrets', stdout=out)
        self.assertIn('1 unreadable', out.getvalue())
        self.assertEqual(
            MarketingSettings.objects.get(pk=self.marketing.pk).twilio_auth_token_encrypted, stored)

    def test_does_nothing_without_an_old_key(self):
        out = StringIO()
        with override_settings(SECRET_KEY=NEW, OLD_SECRET_KEY=''):
            call_command('reencrypt_secrets', stdout=out)
        self.assertEqual(out.getvalue(), '')
        with override_settings(SECRET_KEY=OLD, OLD_SECRET_KEY=''):
            self.assertEqual(self._read(), self._expected())
