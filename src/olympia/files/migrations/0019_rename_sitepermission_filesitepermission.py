# Generated by Django 3.2.9 on 2021-12-02 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0018_auto_20211130_1539'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SitePermission',
            new_name='FileSitePermission',
        ),
    ]
