# Generated by Django 4.2.5 on 2023-10-03 14:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import olympia.amo.models


class Migration(migrations.Migration):
    dependencies = [
        ('abuse', '0009_abusereport_reporter_email_name_reasons'),
    ]

    operations = [
        migrations.CreateModel(
            name='CinderReport',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created',
                    models.DateTimeField(
                        blank=True, default=django.utils.timezone.now, editable=False
                    ),
                ),
                ('modified', models.DateTimeField(auto_now=True)),
                ('job_id', models.CharField(max_length=36)),
                (
                    'decision_action',
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, 'No decision'),
                            (1, 'User ban'),
                            (2, 'Add-on disable'),
                            (3, 'Escalate add-on to reviewers'),
                            (4, 'Escalate add-on to reviewers'),
                            (5, 'Rating delete'),
                            (6, 'Collection delete'),
                            (7, 'Approved (no action)'),
                        ],
                        default=0,
                    ),
                ),
                (
                    'decision_id',
                    models.CharField(default=None, max_length=36, null=True),
                ),
                (
                    'abuse_report',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='abuse.abusereport',
                    ),
                ),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
    ]
