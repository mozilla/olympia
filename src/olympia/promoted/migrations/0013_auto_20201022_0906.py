# Generated by Django 2.2.16 on 2020-10-22 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promoted', '0012_auto_20201022_0903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotedsubscription',
            name='payment_cancelled_at',
            field=models.DateTimeField(help_text='This date is set when the developer has cancelled the initial payment process.', null=True),
        ),
        migrations.AlterField(
            model_name='promotedsubscription',
            name='payment_completed_at',
            field=models.DateTimeField(help_text='This date is set when the developer has successfully completed the initial payment process.', null=True),
        ),
    ]
