# Generated by Django 2.2.5 on 2019-09-12 13:35

from django.db import migrations, models
import django.utils.timezone
import olympia.amo.fields
import olympia.amo.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', olympia.amo.fields.PositiveAutoField(primary_key=True, serialize=False)),
                ('application', models.PositiveIntegerField(choices=[(1, 'Firefox'), (61, 'Firefox for Android')], db_column='application_id')),
                ('version', models.CharField(default='', max_length=255)),
                ('version_int', models.BigIntegerField(editable=False)),
            ],
            options={
                'db_table': 'appversions',
                'ordering': ['-version_int'],
            },
            bases=(olympia.amo.models.SearchMixin, olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.AddIndex(
            model_name='appversion',
            index=models.Index(fields=['application'], name='application_id'),
        ),
        migrations.AddIndex(
            model_name='appversion',
            index=models.Index(fields=['version'], name='version'),
        ),
        migrations.AddIndex(
            model_name='appversion',
            index=models.Index(fields=['version_int'], name='version_int_idx'),
        ),
        migrations.AddConstraint(
            model_name='appversion',
            constraint=models.UniqueConstraint(fields=('application', 'version'), name='application_id_2'),
        ),
    ]
