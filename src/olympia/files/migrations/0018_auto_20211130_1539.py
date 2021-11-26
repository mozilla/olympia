# Generated by Django 3.2.9 on 2021-11-30 15:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import olympia.amo.models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0017_auto_20211128_0808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='source',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Developer Hub'), (2, 'Signing API'), (3, 'Addon API'), (4, 'Automatically generated')], default=None, null=True),
        ),
        migrations.CreateModel(
            name='SitePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('permissions', models.JSONField(default=list)),
                ('file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='_site_permissions', to='files.file')),
            ],
            options={
                'db_table': 'site_permissions',
            },
            bases=(olympia.amo.models.SearchMixin, olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
    ]
