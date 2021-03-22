# Generated by Django 2.2.18 on 2021-02-23 12:15

from django.db import migrations


def set_all_files_platform_to_all(apps, schema_editor):
    PLATFORM_ALL = 0
    File = apps.get_model('files', 'File')
    # At this point we should no longer have more than one File per Version.
    # We already set platform=ALL on Files on Versions that did have duplicate
    # Files, and we've been setting it for new Files for a while now as well,
    # now we need to do it for all the rest of them.
    File.objects.exclude(platform=PLATFORM_ALL).update(platform=PLATFORM_ALL)


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0005_auto_20201120_0926'),
    ]

    operations = [
        migrations.RunPython(set_all_files_platform_to_all)
    ]
