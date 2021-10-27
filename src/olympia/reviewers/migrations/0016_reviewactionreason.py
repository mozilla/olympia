# Generated by Django 3.2.8 on 2021-10-27 18:30

from django.db import migrations, models
import django.utils.timezone
import olympia.amo.fields
import olympia.amo.models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewers', '0015_auto_20210511_1256'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewActionReason',
            fields=[
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', olympia.amo.fields.PositiveAutoField(primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True, help_text='Is available to be assigned to an action')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'reviewactionreason',
            },
            bases=(olympia.amo.models.SearchMixin, olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
    ]
