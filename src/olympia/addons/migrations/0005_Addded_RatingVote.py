# Generated by Django 2.2.10 on 2020-03-29 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0004_auto_20191126_1712'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='addoncategory',
            name='feature_addon_idx',
        ),
        migrations.RemoveField(
            model_name='addoncategory',
            name='feature',
        ),
        migrations.RemoveField(
            model_name='addoncategory',
            name='feature_locales',
        ),
    ]
