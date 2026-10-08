"""Check every project's live app once and record the results.

Run it on a schedule (for example a Railway cron service every five minutes)
so uptime reflects the whole day, not just the moments someone has Operate
open. Projects checked within the last few minutes are skipped.
"""

from django.core.management.base import BaseCommand

from apps.Imagi.Operate.models import AppMonitor
from apps.Imagi.Operate.services import monitoring


class Command(BaseCommand):
    help = "Check each project's live app address for uptime and response time."

    def handle(self, *args, **options):
        monitors = (
            AppMonitor.objects.select_related('project')
            .exclude(live_url='')
            .filter(project__is_active=True)
        )
        checked = 0
        for monitor in monitors.iterator():
            if not monitoring.check_is_stale(monitor):
                continue
            result = monitoring.run_check(monitor)
            checked += 1
            self.stdout.write(f"{monitor.live_url}: {'up' if result.is_up else 'down'}")
        self.stdout.write(self.style.SUCCESS(f'Checked {checked} app(s).'))
