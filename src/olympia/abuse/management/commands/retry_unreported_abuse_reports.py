from django.core.management.base import BaseCommand

import olympia.core.logger
from olympia.abuse.models import AbuseReport, AbuseReportManager
from olympia.abuse.tasks import report_to_cinder


class Command(BaseCommand):
    log = olympia.core.logger.getLogger('z.abuse')

    def handle(self, *args, **options):
        qs = AbuseReport.objects.filter(
            AbuseReportManager.is_individually_actionable_q(), cinder_job__isnull=True
        )
        self.stdout.write(f'{len(qs)} AbuseReports to report to Cinder')

        for report in qs:
            # call task to fire off cinder report
            self.log.info('Created task for %s.', report)
            report_to_cinder.delay(report.id)
