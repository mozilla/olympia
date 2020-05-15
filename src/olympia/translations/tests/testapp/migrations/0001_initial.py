# Generated by Django 2.2.5 on 2019-09-17 13:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import olympia.amo.models
import olympia.translations.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('translations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContainsManyToManyToTranslatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UntranslatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('number', models.IntegerField()),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TranslatedModelWithDefaultNull',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', olympia.translations.fields.TranslatedField(blank=True, db_column='name', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                                     related_name='TranslatedModelWithDefaultNull_name_set+', require_locale=True, short=True, to='translations.Translation', to_field='id', unique=True)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TranslatedModelLinkedAsForeignKey',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', olympia.translations.fields.TranslatedField(blank=True, db_column='name', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                                     related_name='TranslatedModelLinkedAsForeignKey_name_set+', require_locale=True, short=True, to='translations.Translation', to_field='id', unique=True)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TranslatedModel',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('default_locale', models.CharField(max_length=10)),
                ('description', olympia.translations.fields.TranslatedField(blank=True, db_column='description', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                                            related_name='TranslatedModel_description_set+', require_locale=True, short=True, to='translations.Translation', to_field='id', unique=True)),
                ('name', olympia.translations.fields.TranslatedField(blank=True, db_column='name', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                                     related_name='TranslatedModel_name_set+', require_locale=True, short=True, to='translations.Translation', to_field='id', unique=True)),
                ('no_locale', olympia.translations.fields.TranslatedField(blank=True, db_column='no_locale', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                                          related_name='TranslatedModel_no_locale_set+', require_locale=False, short=True, to='translations.Translation', to_field='id', unique=True)),
                ('translated_through_fk', models.ForeignKey(default=None, null=True,
                                                            on_delete=django.db.models.deletion.CASCADE, to='testapp.TranslatedModelLinkedAsForeignKey')),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FancyModel',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('linkified', olympia.translations.fields.LinkifiedField(blank=True, db_column='linkified', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                                         related_name='FancyModel_linkified_set+', require_locale=True, short=True, to='translations.LinkifiedTranslation', to_field='id', unique=True)),
                ('purified', olympia.translations.fields.PurifiedField(blank=True, db_column='purified', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                                       related_name='FancyModel_purified_set+', require_locale=True, short=True, to='translations.PurifiedTranslation', to_field='id', unique=True)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ContainsTranslatedThrough',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True,
                                                 default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('container', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                to='testapp.ContainsManyToManyToTranslatedModel')),
                ('target', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='testapp.TranslatedModel')),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SearchMixin,
                   olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.AddField(
            model_name='containsmanytomanytotranslatedmodel',
            name='things',
            field=models.ManyToManyField(
                through='testapp.ContainsTranslatedThrough', to='testapp.TranslatedModel'),
        ),
    ]
