# Generated by Django 2.2.9 on 2020-01-28 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scanners', '0023_auto_20200122_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scannerqueryresult',
            name='state',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(None, 'Unknown'), (
                1, 'True positive'), (2, 'False positive'), (3, 'Inconclusive')], default=None, null=True),
        ),
        migrations.AlterField(
            model_name='scannerresult',
            name='state',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(None, 'Unknown'), (
                1, 'True positive'), (2, 'False positive'), (3, 'Inconclusive')], default=None, null=True),
        ),
    ]
