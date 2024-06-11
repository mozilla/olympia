# Generated by Django 4.2.13 on 2024-06-11 09:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bandwagon', '0001_initial'),
        ('ratings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('abuse', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cinderdecision',
            name='rating',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ratings.rating'),
        ),
        migrations.AddField(
            model_name='cinderdecision',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='abusereport',
            name='appellant_job',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appellants', to='abuse.cinderjob'),
        ),
        migrations.AddField(
            model_name='abusereport',
            name='cinder_job',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='abuse.cinderjob'),
        ),
        migrations.AddField(
            model_name='abusereport',
            name='collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='abuse_reports', to='bandwagon.collection'),
        ),
        migrations.AddField(
            model_name='abusereport',
            name='rating',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='abuse_reports', to='ratings.rating'),
        ),
        migrations.AddField(
            model_name='abusereport',
            name='reporter',
            field=models.ForeignKey(blank=True, help_text='The user who submitted the report, if authenticated.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='abuse_reported', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='abusereport',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='abuse_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='cinderdecision',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('addon__isnull', False), ('collection__isnull', True), ('rating__isnull', True), ('user__isnull', True)), models.Q(('addon__isnull', True), ('collection__isnull', True), ('rating__isnull', True), ('user__isnull', False)), models.Q(('addon__isnull', True), ('collection__isnull', True), ('rating__isnull', False), ('user__isnull', True)), models.Q(('addon__isnull', True), ('collection__isnull', False), ('rating__isnull', True), ('user__isnull', True)), _connector='OR'), name='just_one_of_addon_user_rating_collection_must_be_set'),
        ),
        migrations.AddIndex(
            model_name='abusereport',
            index=models.Index(fields=['created'], name='abuse_reports_created_idx'),
        ),
        migrations.AddIndex(
            model_name='abusereport',
            index=models.Index(fields=['guid'], name='guid_idx'),
        ),
        migrations.AddConstraint(
            model_name='abusereport',
            constraint=models.CheckConstraint(check=models.Q(models.Q(models.Q(('guid', ''), _negated=True), ('collection__isnull', True), ('guid__isnull', False), ('rating__isnull', True), ('user__isnull', True)), models.Q(('collection__isnull', True), ('guid__isnull', True), ('rating__isnull', True), ('user__isnull', False)), models.Q(('collection__isnull', True), ('guid__isnull', True), ('rating__isnull', False), ('user__isnull', True)), models.Q(('collection__isnull', False), ('guid__isnull', True), ('rating__isnull', True), ('user__isnull', True)), _connector='OR'), name='just_one_of_guid_user_rating_collection_must_be_set'),
        ),
    ]
