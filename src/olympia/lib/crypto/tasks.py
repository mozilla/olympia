import json
import os
import zipfile

from django.db import transaction

import olympia.core.logger
from olympia import amo
from olympia.activity.models import ActivityLog
from olympia.addons.models import Addon, AddonUser
from olympia.amo.celery import task
from olympia.files.models import FileUpload
from olympia.files.utils import parse_addon
from olympia.lib.crypto.signing import sign_file
from olympia.users.utils import get_task_user
from olympia.versions.compare import VersionString
from olympia.versions.models import Version


log = olympia.core.logger.getLogger('z.task')


MAIL_COSE_SUBJECT = 'Your Firefox add-on has been re-signed'

MAIL_COSE_MESSAGE = """
Greetings from the Firefox Add-ons team!

Per our previous communication, this email is to confirm that the most recent
publicly available version of your add-on has now been re-signed with a
stronger signature for a more secure add-ons ecosystem. It will remain
backwards compatible with previous versions of Firefox.

Please be aware that to re-sign add-ons automatically we had to clone the
latest public version of your add-on, bump the version number and then re-sign,
so don’t be alarmed if you see that your add-on’s version number has increased.

Please feel free to reply to this email if you have any questions.

Regards,
Firefox Add-ons team
"""  # noqa: E501


def get_new_version_number(version):
    # Parse existing version number, increment the last part, and replace
    # the suffix with "resigned1", in order to get a new version number that
    # would force existing users to upgrade while making it explicit this is
    # an automatic re-sign. For example, '1.0' would return '1.1resigned1'.
    vs = VersionString(version)
    parts = vs.vparts
    # We're always incrementing the last "number".
    parts[-1].a += 1
    # The "suffix" is always "resigned1" (potentially overriding whatever was
    # there).
    parts[-1].b = 'resigned'
    parts[-1].c = 1
    return VersionString('.'.join(str(part) for part in parts))


def update_version_in_json_manifest(content, new_version_number):
    """Change the version number in the json manifest file provided."""
    updated = json.loads(content)
    if 'version' in updated:
        updated['version'] = new_version_number
    return json.dumps(updated)


def copy_bumping_version_number(src, dst, new_version_number):
    """Copy a xpi while bumping its version number in the manifest."""
    # We can't modify the contents of a zipfile in-place, so instead of copying
    # the old zip file and modifying it, we open the old one, copy the contents
    # of each file it contains to the new one, altering the manifest.json when
    # we run into it.
    os.makedirs(os.path.dirname(dst))
    with zipfile.ZipFile(src, 'r') as source:
        file_list = source.infolist()
        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as dest:
            for file_ in file_list:
                content = source.read(file_.filename)
                if file_.filename == 'manifest.json':
                    content = update_version_in_json_manifest(
                        content, new_version_number
                    )
                dest.writestr(file_, content)


@task
def sign_addons(addon_ids):
    """Used to sign all the versions of an addon.

    This is used in the 'process_addons --task resign_addons_for_cose'
    management command.

    This is also used to resign some promoted addons after they've been added
    to a group (or paid).

    It also bumps the version number of the file and the Version, so the
    Firefox extension update mechanism picks this new signed version and
    installs it.
    """
    log.info(f'[{len(addon_ids)}] Signing addons.')

    mail_subject, mail_message = MAIL_COSE_SUBJECT, MAIL_COSE_MESSAGE

    current_versions = Addon.objects.filter(id__in=addon_ids).values_list(
        '_current_version', flat=True
    )
    qs = Version.objects.filter(id__in=current_versions)

    task_user = get_task_user()

    for old_version in qs:
        addon = old_version.addon
        old_file_obj = old_version.file
        # We only sign files that have been reviewed
        if old_file_obj.status not in amo.APPROVED_STATUSES:
            log.info(
                'Not signing addon {}, version {} (no files)'.format(
                    old_version.addon, old_version
                )
            )
            continue

        log.info(f'Bumping addon {old_version.addon}, version {old_version}')
        bumped_version_number = get_new_version_number(old_version.version)
        did_sign = False  # Did we sign at the file?

        if not old_file_obj.file or not os.path.isfile(old_file_obj.file.path):
            log.info(f'File {old_file_obj.pk} does not exist, skip')
            continue

        old_validation = (
            old_file_obj.validation.validation
            if old_file_obj.has_been_validated
            else None
        )

        try:
            # Copy the original file to a new FileUpload.
            task_user = get_task_user()
            # last login ip should already be set in the database even on the
            # task user, but in case it's not, like in tests/local envs, set it
            # on the instance, forcing it to be localhost, that should be
            # enough for our needs.
            task_user.last_login_ip = '127.0.0.1'
            original_author = addon.authors.first()
            upload = FileUpload.objects.create(
                addon=addon,
                version=bumped_version_number,
                user=task_user,
                channel=amo.CHANNEL_LISTED,
                source=amo.UPLOAD_SOURCE_GENERATED,
                ip_address=task_user.last_login_ip,
                validation=old_validation,
            )
            upload.name = f'{upload.uuid.hex}_{bumped_version_number}.zip'
            upload.path = upload.generate_path('.zip')
            upload.valid = True
            upload.save()

            # Create the xpi with the bumped version number.
            copy_bumping_version_number(
                old_file_obj.file.path, upload.file_path, bumped_version_number
            )

            # Parse the add-on. We use the original author of the add-on, not
            # the task user, in case they have special permissions allowing
            # the original version to be submitted.
            parsed_data = parse_addon(upload, addon=addon, user=original_author)
            parsed_data['approval_notes'] = old_version.approval_notes

            with transaction.atomic():
                # Create a version object out of the FileUpload + parsed data.
                new_version = Version.from_upload(
                    upload,
                    old_version.addon,
                    compatibility=old_version.compatible_apps,
                    channel=amo.CHANNEL_LISTED,
                    parsed_data=parsed_data,
                )

                # Sign it (may raise SigningError).
                sign_file(new_version.file)

                # Approve it.
                new_version.file.update(
                    approval_date=new_version.file.created,
                    datestatuschanged=new_version.file.created,
                    status=amo.STATUS_APPROVED,
                )

        except Exception:
            log.exception(f'Failed re-signing file {old_file_obj.pk}', exc_info=True)

        # Now update the Version model, if we signed at least one file.
        if did_sign:
            ActivityLog.objects.create(
                amo.LOG.VERSION_RESIGNED,
                addon,
                new_version,
                str(old_version.version),
                user=task_user,
            )
            # Send a mail to the owners warning them we've automatically
            # created and signed a new version of their addon.
            qs = AddonUser.objects.filter(
                role=amo.AUTHOR_ROLE_OWNER, addon=addon
            ).exclude(user__email__isnull=True)
            emails = qs.values_list('user__email', flat=True)
            subject = mail_subject
            message = mail_message.format(addon=addon.name)
            amo.utils.send_mail(
                subject,
                message,
                recipient_list=emails,
                headers={'Reply-To': 'amo-admins@mozilla.com'},
            )
