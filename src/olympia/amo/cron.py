from datetime import date, datetime, timedelta

from django.core.files.storage import default_storage as storage

import olympia.core.logger
from olympia import amo
from olympia.activity.models import ActivityLog
from olympia.addons.models import Addon
from olympia.addons.tasks import delete_addons
from olympia.amo.models import FakeEmail, Metric
from olympia.amo.utils import chunked
from olympia.constants.activity import RETENTION_DAYS
from olympia.constants.promoted import NOT_PROMOTED, PROMOTED_GROUPS
from olympia.files.models import FileUpload
from olympia.reviewers.views import (
    PendingManualApprovalQueueTable,
    reviewer_tables_registry,
)
from olympia.scanners.models import ScannerResult

from . import tasks
from .sitemap import (
    get_sitemap_path,
    get_sitemap_section_pages,
    get_sitemaps,
    render_index_xml,
)


log = olympia.core.logger.getLogger('z.cron')


def gc(test_result=True):
    """Site-wide garbage collections."""

    def days_ago(days):
        return datetime.today() - timedelta(days=days)

    log.info('Collecting data to delete')

    logs = (
        ActivityLog.objects.filter(created__lt=days_ago(RETENTION_DAYS))
        .exclude(action__in=amo.LOG_KEEP)
        .values_list('id', flat=True)
    )

    for chunk in chunked(logs, 100):
        tasks.delete_logs.delay(chunk)

    two_weeks_ago = days_ago(15)
    # Hard-delete stale add-ons with no versions. No email should be sent.
    versionless_addons = Addon.unfiltered.filter(
        versions__pk=None, created__lte=two_weeks_ago
    ).values_list('pk', flat=True)
    for chunk in chunked(versionless_addons, 100):
        delete_addons.delay(chunk, with_deleted=True, deny_guids=False)

    # Delete stale FileUploads.
    stale_uploads = FileUpload.objects.filter(created__lte=two_weeks_ago).order_by('id')
    for file_upload in stale_uploads:
        log.info(
            '[FileUpload:{uuid}] Removing file: {path}'.format(
                uuid=file_upload.uuid, path=file_upload.file_path
            )
        )
        if file_upload.file_path:
            try:
                storage.delete(file_upload.file_path)
            except OSError:
                pass
        file_upload.delete()

    # Delete stale ScannerResults.
    ScannerResult.objects.filter(upload=None, version=None).delete()

    # Delete fake emails older than 90 days
    FakeEmail.objects.filter(created__lte=days_ago(90)).delete()


def write_sitemaps(section=None, app_name=None):
    index_filename = get_sitemap_path(None, None)
    sitemaps = get_sitemaps()
    if (not section or section == 'index') and not app_name:
        with storage.open(index_filename, 'w') as index_file:
            log.info('Writing sitemap index')
            index_file.write(render_index_xml(sitemaps))
    for _section, _app_name, _page in get_sitemap_section_pages(sitemaps):
        if (section and section != _section) or (app_name and app_name != _app_name):
            continue
        if _page % 1000 == 1:
            # log an info message every 1000 pages in a _section, _app_name
            log.info(f'Writing sitemap file for {_section}, {_app_name}, {_page}')
        filename = get_sitemap_path(_section, _app_name, _page)
        with storage.open(filename, 'w') as sitemap_file:
            sitemap_object = sitemaps.get((_section, amo.APPS.get(_app_name)))
            if not sitemap_object:
                continue
            content = sitemap_object.render(app_name=_app_name, page=_page)
            sitemap_file.write(content)


def record_metrics():
    today = date.today()
    # Grab a queryset for each reviewer queue.
    querysets = {
        queue.name: queue.get_queryset(None)
        for queue in reviewer_tables_registry.values()
    }
    # Also drill down manual review queue by promoted class (there is no real
    # queue for each, but we still want that data).
    for group in PROMOTED_GROUPS:
        if group != NOT_PROMOTED:
            querysets[f'{PendingManualApprovalQueueTable.name}/{group.api_name}'] = (
                PendingManualApprovalQueueTable.get_queryset(
                    None
                ).filter(promotedaddon__group_id=group.id)
            )

    # Execute a count for each queryset and record a Metric instance for it.
    for key, qs in querysets.items():
        Metric.objects.get_or_create(
            name=key, date=today, defaults={'value': qs.optimized_count()}
        )
