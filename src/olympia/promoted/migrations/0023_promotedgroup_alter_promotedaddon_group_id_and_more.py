# Generated by Django 4.2.18 on 2025-02-04 19:21


from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import olympia.amo.models

from olympia.constants.promoted import PROMOTED_GROUPS_BY_ID

def create_promoted_groups(apps, schema_editor):
    PromotedGroup = apps.get_model('promoted', 'PromotedGroup')
    # Import legacy promoted groups from constants

    # Loop over all groups (active and inactive) from PROMOTED_GROUPS_BY_ID
    for group in PROMOTED_GROUPS_BY_ID.values():
        PromotedGroup.objects.create(
            group_id=group.id,
            name=group.name,
            api_name=group.api_name,
            search_ranking_bump=group.search_ranking_bump,
            listed_pre_review=group.listed_pre_review,
            unlisted_pre_review=group.unlisted_pre_review,
            admin_review=group.admin_review,
            badged=group.badged,
            autograph_signing_states=group.autograph_signing_states,
            can_primary_hero=group.can_primary_hero,
            immediate_approval=group.immediate_approval,
            flag_for_human_review=group.flag_for_human_review,
            can_be_compatible_with_all_fenix_versions=group.can_be_compatible_with_all_fenix_versions,
            high_profile=group.high_profile,
            high_profile_rating=group.high_profile_rating,
            # We only include actively promoted groups so we can hardcode to true
            active=True,
        )


def reverse_promoted_groups(apps, schema_editor):
    PromotedGroup = apps.get_model('promoted', 'PromotedGroup')
    PromotedGroup.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('promoted', '0022_alter_promotedaddon_group_id_and_more'),
    ]

    operations = [
        # 1. Create the new models
        migrations.CreateModel(
            name='PromotedGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.SmallIntegerField(choices=[(0, 'Not Promoted'), (1, 'Recommended'), (4, 'By Firefox'), (5, 'Spotlight'), (6, 'Strategic'), (7, 'Notable'), (8, 'Sponsored'), (9, 'Verified')], help_text='The legacy  ID from back when promoted groups were static classes')),
                ('name', models.CharField(help_text='Human-readable name for the promotion group.', max_length=255)),
                ('api_name', models.CharField(help_text='Programmatic API name for the promotion group.', max_length=100)),
                ('search_ranking_bump', models.FloatField(default=0.0, help_text='Boost value used to influence search ranking for add-ons in this group.')),
                ('listed_pre_review', models.BooleanField(default=False, help_text='Indicates if listed versions require pre-review.')),
                ('unlisted_pre_review', models.BooleanField(default=False, help_text='Indicates if unlisted versions require pre-review.')),
                ('admin_review', models.BooleanField(default=False, help_text='Specifies whether the promotion requires administrative review.')),
                ('badged', models.BooleanField(default=False, help_text='Specifies if the add-on receives a badge upon promotion.')),
                ('autograph_signing_states', models.JSONField(default=dict, help_text='Mapping of application shorthand to autograph signing states.')),
                ('can_primary_hero', models.BooleanField(default=False, help_text='Determines if the add-on can be featured in a primary hero shelf.')),
                ('immediate_approval', models.BooleanField(default=False, help_text='If true, add-ons are auto-approved upon saving.')),
                ('flag_for_human_review', models.BooleanField(default=False, help_text='If true, add-ons are flagged for manual human review.')),
                ('can_be_compatible_with_all_fenix_versions', models.BooleanField(default=False, help_text='Determines compatibility with all Fenix (Android) versions.')),
                ('high_profile', models.BooleanField(default=False, help_text='Indicates if the add-on is high-profile for review purposes.')),
                ('high_profile_rating', models.BooleanField(default=False, help_text='Indicates if developer replies are treated as high-profile.')),
                ('active', models.BooleanField(default=False, help_text='Marks whether this promotion group is active (inactive groups are considered obsolete).')),
            ],
        ),
        migrations.CreateModel(
            name='PromotedAddonPromotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('application_id', models.SmallIntegerField(choices=[(1, 'Firefox'), (61, 'Firefox for Android')], verbose_name='Application')),
                ('addon', models.ForeignKey(help_text='Add-on id this item will point to (If you do not know the id, paste the slug instead and it will be transformed automatically for you. If you have access to the add-on admin page, you can use the magnifying glass to see all available add-ons.', on_delete=django.db.models.deletion.CASCADE, to='addons.addon')),
                ('promoted_group', models.ForeignKey(help_text='Can be set to Not Promoted to disable promotion without deleting it.  Note: changing the group does *not* change approvals of versions.', on_delete=django.db.models.deletion.CASCADE, to='promoted.promotedgroup')),
            ],
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PromotedAddonVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('promoted_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promoted_versions', to='promoted.promotedgroup')),
                ('application_id', models.SmallIntegerField(choices=[(1, 'Firefox'), (61, 'Firefox for Android')], verbose_name='Application')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promoted_versions', to='versions.version')),
            ],
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        # 2. Add constraints on the new tables that match the legacy tables.
        # This is to support full sync compatibility between the two models
        # until we have ported all code references to the new models.
        migrations.AddConstraint(
            model_name='promotedaddonpromotion',
            constraint=models.UniqueConstraint(fields=('addon', 'application_id'), name='unique_promoted_addon_application'),
        ),
        migrations.AddConstraint(
            model_name='promotedaddonversion',
            constraint=models.UniqueConstraint(fields=('promoted_group', 'application_id', 'version'), name='unique_promoted_addon_version'),
        ),
        # 3. Finally we can populate the PromotedGroup instances since they
        # are static and do not frequently change.
        migrations.RunPython(create_promoted_groups, reverse_promoted_groups),
    ]
