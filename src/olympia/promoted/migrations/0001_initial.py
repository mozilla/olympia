# Generated by Django 4.2.13 on 2024-06-11 09:37

from django.db import migrations, models
import django.utils.timezone
import olympia.amo.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PromotedAddon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('group_id', models.SmallIntegerField(choices=[(0, 'Not Promoted'), (1, 'Recommended'), (2, 'Sponsored'), (3, 'Verified'), (4, 'By Firefox'), (5, 'Spotlight'), (6, 'Strategic'), (7, 'Notable')], default=0, help_text='Can be set to Not Promoted to disable promotion without deleting it.  Note: changing the group does *not* change approvals of versions.', verbose_name='Group')),
                ('application_id', models.SmallIntegerField(blank=True, choices=[(None, 'All Applications'), (1, 'Firefox'), (61, 'Firefox for Android')], null=True, verbose_name='Application')),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PromotedApproval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('group_id', models.SmallIntegerField(choices=[(1, 'Recommended'), (2, 'Sponsored'), (3, 'Verified'), (4, 'By Firefox'), (5, 'Spotlight'), (7, 'Notable')], null=True, verbose_name='Group')),
                ('application_id', models.SmallIntegerField(choices=[(1, 'Firefox'), (61, 'Firefox for Android')], default=None, null=True, verbose_name='Application')),
            ],
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
    ]
