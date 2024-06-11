# Generated by Django 4.2.13 on 2024-06-11 09:37

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import olympia.amo.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('addons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitExtractionEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('in_progress', models.BooleanField(default=None, null=True)),
                ('addon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='addons.addon')),
            ],
            options={
                'verbose_name_plural': 'Git extraction entries',
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
                'unique_together': {('addon', 'in_progress')},
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
    ]
