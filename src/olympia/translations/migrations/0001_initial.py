# Generated by Django 4.2.13 on 2024-06-11 09:37

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
            name='Translation',
            fields=[
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('autoid', olympia.amo.fields.PositiveAutoField(primary_key=True, serialize=False)),
                ('id', models.PositiveIntegerField()),
                ('locale', models.CharField(max_length=10)),
                ('localized_string', models.TextField(null=True)),
                ('localized_string_clean', models.TextField(null=True)),
            ],
            options={
                'db_table': 'translations',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TranslationSequence',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'translations_seq',
            },
        ),
        migrations.AddConstraint(
            model_name='translation',
            constraint=models.UniqueConstraint(fields=('id', 'locale'), name='id'),
        ),
        migrations.CreateModel(
            name='NoURLsTranslation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('translations.translation',),
        ),
        migrations.CreateModel(
            name='PurifiedTranslation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('translations.translation',),
        ),
        migrations.CreateModel(
            name='LinkifiedTranslation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('translations.purifiedtranslation',),
        ),
    ]
