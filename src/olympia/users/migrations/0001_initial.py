# Generated by Django 4.2.13 on 2024-06-11 09:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import olympia.amo.fields
import olympia.amo.models
import olympia.amo.validators
import olympia.users.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('addons', '0001_initial'),
        ('bandwagon', '0001_initial'),
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(default=olympia.users.models.get_anonymized_username, max_length=255, unique=True)),
                ('display_name', models.CharField(blank=True, default='', max_length=50, null=True, validators=[django.core.validators.MinLengthValidator(2), olympia.amo.validators.OneOrMorePrintableCharacterValidator()])),
                ('email', models.EmailField(max_length=75, null=True, unique=True)),
                ('averagerating', models.FloatField(null=True)),
                ('biography', models.CharField(blank=True, max_length=255, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('display_collections', models.BooleanField(default=False)),
                ('homepage', models.URLField(blank=True, default='', max_length=255)),
                ('location', models.CharField(blank=True, default='', max_length=255)),
                ('notes', models.TextField(blank=True, null=True)),
                ('occupation', models.CharField(blank=True, default='', max_length=255)),
                ('picture_type', models.CharField(blank=True, default=None, max_length=75, null=True)),
                ('read_dev_agreement', models.DateTimeField(blank=True, null=True)),
                ('last_login_ip', models.CharField(default='', editable=False, max_length=45)),
                ('email_changed', models.DateTimeField(editable=False, null=True)),
                ('banned', models.DateTimeField(editable=False, null=True)),
                ('is_public', models.BooleanField(db_column='public', default=False)),
                ('fxa_id', models.CharField(blank=True, max_length=128, null=True)),
                ('auth_id', models.PositiveIntegerField(default=olympia.users.models.generate_auth_id, null=True)),
                ('basket_token', models.CharField(blank=True, default='', max_length=128)),
                ('bypass_upload_restrictions', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'users',
            },
            bases=(olympia.amo.models.OnChangeMixin, olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DeniedName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(default='', max_length=255, unique=True)),
            ],
            options={
                'db_table': 'users_denied_name',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DisposableEmailDomainRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('restriction_type', models.PositiveSmallIntegerField(choices=[(1, 'Add-on Submission'), (2, 'Add-on Approval'), (3, 'Rating'), (4, 'Rating Flag for Moderation')], default=1)),
                ('reason', models.CharField(blank=True, help_text='Private description of why this restriction was added.', max_length=255, null=True)),
                ('domain', models.CharField(help_text='Enter full disposable email domain that should be blocked. Wildcards are not supported: if you need those, or need to match against the entire email and not just the domain part, use "Email user restrictions" instead.', max_length=255, unique=True)),
            ],
            options={
                'db_table': 'users_disposable_email_domain_restriction',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model, olympia.users.models.RestrictionAbstractBase),
        ),
        migrations.CreateModel(
            name='EmailUserRestriction',
            fields=[
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('restriction_type', models.PositiveSmallIntegerField(choices=[(1, 'Add-on Submission'), (2, 'Add-on Approval'), (3, 'Rating'), (4, 'Rating Flag for Moderation')], default=1)),
                ('reason', models.CharField(blank=True, help_text='Private description of why this restriction was added.', max_length=255, null=True)),
                ('id', olympia.amo.fields.PositiveAutoField(primary_key=True, serialize=False)),
                ('email_pattern', models.CharField(help_text='Enter full email that should be blocked or use unix-style wildcards, e.g. "*@example.com". If you need to block a domain incl subdomains, add a second entry, e.g. "*@*.example.com".', max_length=100, verbose_name='Email Pattern')),
            ],
            options={
                'db_table': 'users_user_email_restriction',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model, olympia.users.models.RestrictionAbstractBase, olympia.users.models.NormalizeEmailMixin),
        ),
        migrations.CreateModel(
            name='IPNetworkUserRestriction',
            fields=[
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('restriction_type', models.PositiveSmallIntegerField(choices=[(1, 'Add-on Submission'), (2, 'Add-on Approval'), (3, 'Rating'), (4, 'Rating Flag for Moderation')], default=1)),
                ('reason', models.CharField(blank=True, help_text='Private description of why this restriction was added.', max_length=255, null=True)),
                ('id', olympia.amo.fields.PositiveAutoField(primary_key=True, serialize=False)),
                ('network', olympia.amo.fields.CIDRField(blank=True, help_text='Enter a valid IPv4 or IPv6 CIDR network range, eg. 127.0.0.1/28', null=True)),
            ],
            options={
                'db_table': 'users_user_network_restriction',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model, olympia.users.models.RestrictionAbstractBase),
        ),
        migrations.CreateModel(
            name='SuppressedEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=75, unique=True)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BannedUserContent',
            fields=[
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='content_disabled_on_ban', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('picture_backup_name', models.CharField(blank=True, default=None, max_length=75, null=True)),
                ('picture_type', models.CharField(blank=True, default=None, max_length=75, null=True)),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserRestrictionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('restriction', models.PositiveSmallIntegerField(choices=[(0, 'DeveloperAgreementRestriction'), (1, 'DisposableEmailDomainRestriction'), (2, 'EmailUserRestriction'), (3, 'IPNetworkUserRestriction'), (4, 'EmailReputationRestriction'), (5, 'IPReputationRestriction')], default=0)),
                ('ip_address', models.CharField(default='', max_length=45)),
                ('last_login_ip', models.CharField(default='', max_length=45)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restriction_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User Restriction History',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('notification_id', models.IntegerField()),
                ('enabled', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_notifications',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', olympia.amo.fields.PositiveAutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=75)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_history',
                'ordering': ('-created',),
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SuppressedEmailVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('confirmation_code', models.CharField(default=uuid.uuid4, max_length=255)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1, 'Delivered'), (2, 'Failed')], default=0)),
                ('suppressed_email', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='suppressed_email', to='users.suppressedemail')),
            ],
            options={
                'get_latest_by': 'created',
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=(olympia.amo.models.SaveUpdateMixin, models.Model),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['created'], name='created'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['fxa_id'], name='users_fxa_id_index'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=olympia.amo.models.LongNameIndex(fields=['last_login_ip'], name='users_last_login_ip_2cfbbfbd'),
        ),
        migrations.AddIndex(
            model_name='userrestrictionhistory',
            index=olympia.amo.models.LongNameIndex(fields=['ip_address'], name='users_userrestrictionhistory_ip_address_4376df32'),
        ),
        migrations.AddIndex(
            model_name='userrestrictionhistory',
            index=olympia.amo.models.LongNameIndex(fields=['last_login_ip'], name='users_userrestrictionhistory_last_login_ip_d58d95ff'),
        ),
        migrations.AddIndex(
            model_name='usernotification',
            index=models.Index(fields=['user'], name='user_id'),
        ),
        migrations.AddIndex(
            model_name='userhistory',
            index=models.Index(fields=['email'], name='users_history_email'),
        ),
        migrations.AddIndex(
            model_name='userhistory',
            index=models.Index(fields=['user'], name='users_history_user_idx'),
        ),
        migrations.AddField(
            model_name='bannedusercontent',
            name='addons',
            field=models.ManyToManyField(to='addons.addon'),
        ),
        migrations.AddField(
            model_name='bannedusercontent',
            name='addons_users',
            field=models.ManyToManyField(to='addons.addonuser'),
        ),
        migrations.AddField(
            model_name='bannedusercontent',
            name='collections',
            field=models.ManyToManyField(to='bandwagon.collection'),
        ),
        migrations.AddField(
            model_name='bannedusercontent',
            name='ratings',
            field=models.ManyToManyField(to='ratings.rating'),
        ),
    ]
