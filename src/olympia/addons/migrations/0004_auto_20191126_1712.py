# Generated by Django 2.2.6 on 2019-11-26 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0003_addonreviewerflags_auto_approval_disabled_until'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addon',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'Extension'), (2, 'Deprecated Complete Theme'), (3, 'Dictionary'), (4, 'Search Engine'), (
                5, 'Language Pack (Application)'), (6, 'Language Pack (Add-on)'), (7, 'Plugin'), (9, 'Deprecated LWT'), (10, 'Theme (Static)')], db_column='addontype_id', default=1),
        ),
        migrations.AlterField(
            model_name='addoncategory',
            name='feature',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='category',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'Extension'), (2, 'Deprecated Complete Theme'), (3, 'Dictionary'), (4, 'Search Engine'), (
                5, 'Language Pack (Application)'), (6, 'Language Pack (Add-on)'), (7, 'Plugin'), (9, 'Deprecated LWT'), (10, 'Theme (Static)')], db_column='addontype_id'),
        ),
    ]
