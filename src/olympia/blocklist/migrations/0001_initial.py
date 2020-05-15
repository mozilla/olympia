# Generated by Django 2.2.6 on 2019-10-23 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import olympia.amo.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('addons', '0002_addon_fk'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('url', models.CharField(blank=True, max_length=255)),
                ('reason', models.TextField(blank=True)),
                ('addon', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='addons.Addon')),
                ('updated_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('max_version', models.CharField(default='*', max_length=255)),
                ('min_version', models.CharField(default='0', max_length=255)),
                ('include_in_legacy', models.BooleanField(default=False)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
    ]
