# Generated by Django 2.2.12 on 2020-05-18 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0004_auto_20191126_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='addonreviewerflags',
            name='notified_about_auto_approval_delay',
            field=models.NullBooleanField(default=False),
        ),
    ]
