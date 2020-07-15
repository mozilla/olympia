# Generated by Django 2.2.14 on 2020-07-15 17:51

from django.db import migrations, models
import olympia.hero.models


def description_from_disco_to_hero(apps, schema_editor):
    PrimaryHero = apps.get_model('hero', 'PrimaryHero')
    qs = PrimaryHero.objects.exclude(disco_addon__custom_description='')
    for ph in qs:
        ph.description = ph.disco_addon.custom_description
        ph.save()


class Migration(migrations.Migration):

    dependencies = [
        ('hero', '0012_auto_20200709_0316'),
    ]

    operations = [
        migrations.AddField(
            model_name='primaryhero',
            name='description',
            field=models.TextField(blank=True, help_text='Text used to describe an add-on. Should not contain any HTML or special tags. Will be translated.'),
        ),
        migrations.RunPython(description_from_disco_to_hero)
    ]
