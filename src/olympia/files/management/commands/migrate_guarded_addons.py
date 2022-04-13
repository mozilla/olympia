import os
from collections import namedtuple
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand


Entry = namedtuple('Entry', 'name, path')


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.migrate()

    def print_eta(self, *, elapsed, remaining_entries):
        # total_seconds() keeps microseconds - it should often be 0.xxxxxx in
        # our case. We use the full precision for computing the ETA, but round
        # to the second when displaying.
        total_seconds = elapsed.total_seconds()
        eta = timedelta(seconds=int(total_seconds * remaining_entries))
        self.stdout.write(f'ETA {eta} ; Remaining entries {remaining_entries}\n')

    def migrate(self):
        guarded_addons_path = os.path.join(settings.STORAGE_ROOT, 'guarded-addons')
        # Note: we handle empty directories, but for ETA to be reliable, it's
        # best to remove them first by running find . -type d -empty -delete.
        total_entries = os.stat(guarded_addons_path).st_nlink - 1
        entries_migrated = 0
        entries = os.scandir(guarded_addons_path)
        for addon in entries:
            if not addon.name.startswith('.'):
                elapsed = self.migrate_addon(Entry(addon.name, addon.path))
                # Since we use the add-ons and not the files to compute the ETA
                # it's never going to be 100% accurate, but it should be good
                # enough.
                entries_migrated += 1
                if entries_migrated == 1 or entries_migrated % 1000 == 0:
                    self.print_eta(
                        elapsed=elapsed,
                        remaining_entries=total_entries - entries_migrated,
                    )

    def migrate_addon(self, addon):
        start_time = datetime.now()
        new_addon_path = os.path.join(settings.ADDONS_PATH, addon.name)
        os.makedirs(new_addon_path, exist_ok=True)
        files = os.scandir(addon.path)
        for file_ in files:
            self.migrate_file(addon, Entry(file_.name, file_.path))
        return datetime.now() - start_time

    def migrate_file(self, addon, file_):
        old_path = file_.path
        new_path = os.path.join(settings.ADDONS_PATH, addon.name, file_.name)
        try:
            os.link(old_path, new_path)
        except FileExistsError:
            # This makes the migration re-runnable, at the expense of making
            # the ETA less accurate for the initial portion we already migrated
            # during a previous pass.
            self.stderr.write(f'Ignoring already existing {old_path}')
