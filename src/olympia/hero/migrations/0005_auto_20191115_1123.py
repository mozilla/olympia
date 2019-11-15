# Generated by Django 2.2.6 on 2019-11-15 11:23

from django.db import migrations
import olympia.hero.models

from . import blank_featured_images


class Migration(migrations.Migration):

    dependencies = [
        ('hero', '0004_auto_20191021_0831'),
    ]

    operations = [
        migrations.RunPython(blank_featured_images),
        migrations.AlterField(
            model_name='primaryhero',
            name='image',
            field=olympia.hero.models.WidgetCharField(blank=True, choices=[('Adnauseum@2x.png', 'Adnauseum@2x.png'), ('Dark Reader 2@2x.png', 'Dark Reader 2@2x.png'), ('Enhancer@2x.png', 'Enhancer@2x.png'), ('Facetainer@2x.png', 'Facetainer@2x.png'), ('Gesturefy@2x.png', 'Gesturefy@2x.png'), ('Ghostery@2x.png', 'Ghostery@2x.png'), ('Google Translate@2x.png', 'Google Translate@2x.png'), ('Privacy Badger@2x.png', 'Privacy Badger@2x.png'), ('Search By Image@2x.png', 'Search By Image@2x.png'), ('Tst1@2x.png', 'Tst1@2x.png'), ('Typing Laptop@2x.png', 'Typing Laptop@2x.png'), ('Ubo@2x.png', 'Ubo@2x.png')], max_length=255),
        ),
    ]
