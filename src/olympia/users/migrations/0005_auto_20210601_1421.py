# Generated by Django 2.2.23 on 2021-06-01 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20201002_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='disposableemaildomainrestriction',
            name='restriction_type',
            field=models.PositiveSmallIntegerField(
                choices=[(1, 'Submission'), (2, 'Approval')], default=1
            ),
        ),
        migrations.AddField(
            model_name='emailuserrestriction',
            name='restriction_type',
            field=models.PositiveSmallIntegerField(
                choices=[(1, 'Submission'), (2, 'Approval')], default=1
            ),
        ),
        migrations.AddField(
            model_name='ipnetworkuserrestriction',
            name='restriction_type',
            field=models.PositiveSmallIntegerField(
                choices=[(1, 'Submission'), (2, 'Approval')], default=1
            ),
        ),
    ]
