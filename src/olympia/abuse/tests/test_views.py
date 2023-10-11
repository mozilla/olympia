import json
from datetime import datetime
from unittest import mock

from django.urls import reverse

from pyquery import PyQuery as pq
from waffle.testutils import override_switch

from olympia import amo
from olympia.abuse.models import AbuseReport, CinderReport
from olympia.amo.tests import (
    APITestClientSessionID,
    TestCase,
    addon_factory,
    get_random_ip,
    reverse_ns,
    user_factory,
)


class AddonAbuseViewSetTestBase:
    client_class = APITestClientSessionID

    def setUp(self):
        self.url = reverse_ns('abusereportaddon-list')

    def check_reporter(self, report):
        raise NotImplementedError

    def check_report(self, report, text):
        assert str(report) == text
        self.check_reporter(report)

    def test_report_addon_by_id(self):
        addon = addon_factory()
        response = self.client.post(
            self.url,
            data={'addon': str(addon.id), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        # It was a public add-on, so we found its guid.
        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.message == 'abuse!'

    def test_report_addon_by_slug(self):
        addon = addon_factory()
        response = self.client.post(
            self.url,
            data={'addon': addon.slug, 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        # It was a public add-on, so we found its guid.
        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)

    def test_report_addon_by_guid(self):
        addon = addon_factory(guid='@badman')
        response = self.client.post(
            self.url,
            data={'addon': addon.guid, 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.message == 'abuse!'

    def test_report_addon_by_id_not_public(self):
        addon = addon_factory(status=amo.STATUS_DISABLED)
        response = self.client.post(
            self.url,
            data={'addon': addon.pk, 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 404

    def test_report_addon_by_slug_not_public(self):
        addon = addon_factory(status=amo.STATUS_DISABLED)
        response = self.client.post(
            self.url,
            data={'addon': addon.slug, 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 404

    def test_report_addon_by_guid_not_public(self):
        addon = addon_factory(guid='@badman', status=amo.STATUS_DISABLED)
        response = self.client.post(
            self.url,
            data={'addon': addon.guid, 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        # We accept any report by guid, even if the add-on is not public or
        # simply inexistant (see test below) since we're not linking them
        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.message == 'abuse!'

    def test_report_addon_guid_not_on_amo(self):
        guid = '@mysteryman'
        response = self.client.post(
            self.url,
            data={'addon': guid, 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(guid=guid).exists()
        report = AbuseReport.objects.get(guid=guid)
        self.check_report(report, 'Abuse Report for Addon %s' % guid)
        assert report.message == 'abuse!'

    def test_report_addon_invalid_identifier(self):
        response = self.client.post(
            self.url, data={'addon': 'randomnotguid', 'message': 'abuse!'}
        )
        assert response.status_code == 404

    def test_addon_not_public(self):
        addon = addon_factory(status=amo.STATUS_NULL)
        response = self.client.post(
            self.url,
            data={'addon': str(addon.id), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        # Fails: for non public add-ons, you have to use the guid.
        assert response.status_code == 404

    def test_addon_not_public_by_guid(self):
        addon = addon_factory(status=amo.STATUS_NULL)
        response = self.client.post(
            self.url,
            data={'addon': str(addon.guid), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.message == 'abuse!'

    def test_no_addon_fails(self):
        response = self.client.post(self.url, data={'message': 'abuse!'})
        assert response.status_code == 400
        assert json.loads(response.content) == {'addon': ['This field is required.']}

    def test_message_required_empty(self):
        addon = addon_factory()
        response = self.client.post(
            self.url, data={'addon': str(addon.id), 'message': ''}
        )
        assert response.status_code == 400
        assert json.loads(response.content) == {
            'message': ['This field may not be blank.']
        }

    def test_message_required_missing(self):
        addon = addon_factory()
        response = self.client.post(self.url, data={'addon': str(addon.id)})
        assert response.status_code == 400
        assert json.loads(response.content) == {'message': ['This field is required.']}

    def test_message_not_required_if_reason_is_provided(self):
        addon = addon_factory()
        response = self.client.post(
            self.url,
            data={'addon': str(addon.id), 'reason': 'broken'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.message == ''

    def test_message_can_be_blank_if_reason_is_provided(self):
        addon = addon_factory()
        response = self.client.post(
            self.url,
            data={'addon': str(addon.id), 'reason': 'broken', 'message': ''},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.message == ''

    def test_message_length_limited(self):
        addon = addon_factory()

        response = self.client.post(
            self.url, data={'addon': str(addon.id), 'message': 'a' * 10000}
        )
        assert response.status_code == 201

        response = self.client.post(
            self.url, data={'addon': str(addon.id), 'message': 'a' * 10001}
        )
        assert response.status_code == 400
        assert json.loads(response.content) == {
            'message': ['Please ensure this field has no more than 10000 characters.']
        }

    def test_throttle(self):
        addon = addon_factory()
        for x in range(20):
            response = self.client.post(
                self.url,
                data={'addon': str(addon.id), 'message': 'abuse!'},
                REMOTE_ADDR='123.45.67.89',
                HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
            )
            assert response.status_code == 201, x

        response = self.client.post(
            self.url,
            data={'addon': str(addon.id), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 429

    def test_optional_fields(self):
        data = {
            'addon': '@mysteryaddon',
            'message': 'This is abusé!',
            'client_id': 'i' * 64,
            'addon_name': 'Addon Næme',
            'addon_summary': 'Addon sûmmary',
            'addon_version': '0.01.01',
            'addon_signature': None,
            'app': 'firefox',
            'appversion': '42.0.1',
            'lang': 'Lô-käl',
            'operating_system': 'Sømething OS',
            'install_date': '2004-08-15T16:23:42',
            'reason': 'spam',
            'addon_install_origin': 'http://example.com/',
            'addon_install_method': 'url',
            'report_entry_point': None,
            'reporter_name': 'Somebody',
            'reporter_email': 'some@body.com',
        }
        response = self.client.post(
            self.url,
            data=data,
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201, response.content

        assert AbuseReport.objects.filter(guid=data['addon']).exists()
        report = AbuseReport.objects.get(guid=data['addon'])
        self.check_report(report, 'Abuse Report for Addon %s' % data['addon'])
        # Straightforward comparisons:
        for field in (
            'message',
            'client_id',
            'addon_name',
            'addon_summary',
            'addon_version',
            'operating_system',
            'addon_install_origin',
            'reporter_name',
            'reporter_email',
        ):
            assert getattr(report, field) == data[field], field
        # More complex comparisons:
        assert report.addon_signature is None
        assert report.application == amo.FIREFOX.id
        assert report.application_version == data['appversion']
        assert report.application_locale == data['lang']
        assert report.install_date == datetime(2004, 8, 15, 16, 23, 42)
        assert report.reason == 2  # Spam / Advertising
        assert report.addon_install_method == (AbuseReport.ADDON_INSTALL_METHODS.URL)
        assert report.addon_install_source is None
        assert report.addon_install_source_url is None
        assert report.report_entry_point is None

    def test_reporter_name_email_reason_fields_can_be_null(self):
        data = {
            'addon': '@mysteryaddon',
            'message': 'This is abusé!',
            'reason': None,
            'reporter_name': None,
            'reporter_email': None,
        }
        response = self.client.post(
            self.url,
            data=data,
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201, response.content

        assert AbuseReport.objects.filter(guid=data['addon']).exists()
        report = AbuseReport.objects.get(guid=data['addon'])
        self.check_report(report, 'Abuse Report for Addon %s' % data['addon'])
        # Straightforward comparisons:
        for field in (
            'reason',
            'reporter_name',
            'reporter_email',
        ):
            assert getattr(report, field) is None

    def test_optional_fields_errors(self):
        data = {
            'addon': '@mysteryaddon',
            'message': 'Message cân be quite big if needed' * 256,
            'client_id': 'i' * 65,
            'addon_name': 'a' * 256,
            'addon_summary': 's' * 256,
            'addon_version': 'v' * 256,
            'addon_signature': 'Something not in signature choices',
            'app': 'FIRE! EXCLAMATION MARK',
            'appversion': '1' * 256,
            'lang': 'l' * 256,
            'operating_system': 'o' * 256,
            'install_date': 'not_a_date',
            'reason': 'Something not in reason choices',
            'addon_install_origin': 'u' * 256,
            'addon_install_method': 'Something not in install method choices',
            'addon_install_source': 'Something not in install source choices',
            'addon_install_source_url': 'http://%s' % 'a' * 249,
            'report_entry_point': 'Something not in entrypoint choices',
            'reporter_name': 'n' * 256,
            'reporter_email': 'not an email address',
        }
        response = self.client.post(
            self.url,
            data=data,
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 400
        expected_max_length_message = (
            'Ensure this field has no more than %d characters.'
        )
        expected_choices_message = '"%s" is not a valid choice.'
        assert response.json() == {
            'client_id': [expected_max_length_message % 64],
            'addon_name': [expected_max_length_message % 255],
            'addon_summary': [expected_max_length_message % 255],
            'addon_version': [expected_max_length_message % 255],
            'addon_signature': [expected_choices_message % data['addon_signature']],
            'app': [expected_choices_message % data['app']],
            'appversion': [expected_max_length_message % 255],
            'lang': [expected_max_length_message % 255],
            'operating_system': [expected_max_length_message % 255],
            'install_date': [
                'Datetime has wrong format. Use one of these formats '
                'instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'
            ],
            'reason': [expected_choices_message % data['reason']],
            'addon_install_origin': [expected_max_length_message % 255],
            'addon_install_source_url': [expected_max_length_message % 255],
            'report_entry_point': [
                expected_choices_message % data['report_entry_point']
            ],
            'reporter_name': [expected_max_length_message % 255],
            'reporter_email': ['Enter a valid email address.'],
        }
        # Note: addon_install_method and addon_install_source silently convert
        # unknown values to "other", so the values submitted here, despite not
        # being valid choices, aren't considered errors. See
        # test_addon_unknown_install_source_and_method() below.

    def test_addon_unknown_install_source_and_method(self):
        data = {
            'addon': '@mysteryaddon',
            'message': 'This is abusé!',
            'addon_install_method': 'something unexpected' * 15,
            'addon_install_source': 'something unexpected indeed',
        }
        response = self.client.post(self.url, data=data)
        assert response.status_code == 201, response.content

        assert AbuseReport.objects.filter(guid=data['addon']).exists()
        report = AbuseReport.objects.get(guid=data['addon'])
        self.check_report(report, 'Abuse Report for Addon %s' % data['addon'])
        assert report.addon_install_method == (AbuseReport.ADDON_INSTALL_METHODS.OTHER)
        assert report.addon_install_source == (AbuseReport.ADDON_INSTALL_SOURCES.OTHER)

    def test_addon_unknown_install_source_and_method_not_string(self):
        addon = addon_factory()
        data = {
            'addon': str(addon.pk),
            'message': 'This is abusé!',
            'addon_install_method': 42,
            'addon_install_source': 53,
        }
        response = self.client.post(self.url, data=data)
        assert response.status_code == 201, response.content

        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.addon_install_method == (AbuseReport.ADDON_INSTALL_METHODS.OTHER)
        assert report.addon_install_source == (AbuseReport.ADDON_INSTALL_SOURCES.OTHER)

    def test_report_country_code(self):
        addon = addon_factory(status=amo.STATUS_NULL)
        response = self.client.post(
            self.url,
            data={'addon': str(addon.guid), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
            HTTP_X_COUNTRY_CODE='YY',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(guid=addon.guid).exists()
        report = AbuseReport.objects.get(guid=addon.guid)
        self.check_report(report, 'Abuse Report for Addon %s' % addon.guid)
        assert report.country_code == 'YY'

    def test_abuse_report_with_invalid_data(self):
        addon = addon_factory()
        # Prepare data with invalid field values
        data = {
            'addon': addon.pk,
            'addon_install_method': {'dictionary_key': 'dictionary_val'},
            'addon_install_source': {'dictionary_key': 'dictionary_val'},
            'message': 'abuse!',
        }

        response = self.client.post(self.url, data=data)
        assert response.status_code == 400
        assert json.loads(response.content) == {'addon_install_method': 'Invalid value'}

    def _setup_reportable_reason(self, reason):
        addon = addon_factory(guid='@badman')
        response = self.client.post(
            self.url,
            data={'addon': addon.guid, 'reason': reason},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 201, response.content

    @mock.patch('olympia.abuse.serializers.report_to_cinder.delay')
    @override_switch('enable-cinder-reporting', active=True)
    def test_reportable_reason_calls_cinder_task(self, task_mock):
        self._setup_reportable_reason('hate_speech')
        task_mock.assert_called()

    @mock.patch('olympia.abuse.serializers.report_to_cinder.delay')
    @override_switch('enable-cinder-reporting', active=False)
    def test_reportable_reason_does_not_call_cinder_with_waffle_off(self, task_mock):
        self._setup_reportable_reason('hate_speech')
        task_mock.assert_not_called()

    @mock.patch('olympia.abuse.serializers.report_to_cinder.delay')
    @override_switch('enable-cinder-reporting', active=True)
    def test_not_reportable_reason_does_not_call_cinder_task(self, task_mock):
        self._setup_reportable_reason('not_wanted')
        task_mock.assert_not_called()


class TestAddonAbuseViewSetLoggedOut(AddonAbuseViewSetTestBase, TestCase):
    def check_reporter(self, report):
        assert not report.reporter


class TestAddonAbuseViewSetLoggedIn(AddonAbuseViewSetTestBase, TestCase):
    def setUp(self):
        super().setUp()
        self.user = user_factory()
        self.client.login_api(self.user)

    def check_reporter(self, report):
        assert report.reporter == self.user

    def test_throttle_ip_for_authenticated_users(self):
        user = user_factory()
        self.client.login_api(user)
        addon = addon_factory()
        for x in range(20):
            response = self.client.post(
                self.url,
                data={'addon': str(addon.id), 'message': 'abuse!'},
                REMOTE_ADDR='123.45.67.89',
                HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
            )
            assert response.status_code == 201, x

        # Different user, same IP: should still be blocked (> 20 / day).
        new_user = user_factory()
        self.client.login_api(new_user)
        response = self.client.post(
            self.url,
            data={'addon': str(addon.id), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 429


class UserAbuseViewSetTestBase:
    client_class = APITestClientSessionID

    def setUp(self):
        self.url = reverse_ns('abusereportuser-list')

    def check_reporter(self, report):
        raise NotImplementedError

    def check_report(self, report, text):
        assert str(report) == text
        self.check_reporter(report)

    def test_report_user_id(self):
        user = user_factory()
        response = self.client.post(
            self.url,
            data={'user': str(user.id), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(user_id=user.id).exists()
        report = AbuseReport.objects.get(user_id=user.id)
        self.check_report(report, 'Abuse Report for User %s' % user)

    def test_report_user_username(self):
        user = user_factory()
        response = self.client.post(
            self.url,
            data={'user': str(user.username), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(user_id=user.id).exists()
        report = AbuseReport.objects.get(user_id=user.id)
        self.check_report(report, 'Abuse Report for User %s' % user)

    def test_no_user_fails(self):
        response = self.client.post(self.url, data={'message': 'abuse!'})
        assert response.status_code == 400
        assert json.loads(response.content) == {'user': ['This field is required.']}

    def test_message_required_empty(self):
        user = user_factory()
        response = self.client.post(
            self.url, data={'user': str(user.username), 'message': ''}
        )
        assert response.status_code == 400
        assert json.loads(response.content) == {
            'message': ['This field may not be blank.']
        }

    def test_message_required_missing(self):
        user = user_factory()
        response = self.client.post(self.url, data={'user': str(user.username)})
        assert response.status_code == 400
        assert json.loads(response.content) == {'message': ['This field is required.']}

    def test_throttle(self):
        user = user_factory()
        for x in range(20):
            response = self.client.post(
                self.url,
                data={'user': str(user.username), 'message': 'abuse!'},
                REMOTE_ADDR='123.45.67.89',
                HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
            )
            assert response.status_code == 201, x

        response = self.client.post(
            self.url,
            data={'user': str(user.username), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 429

    def test_report_country_code(self):
        user = user_factory()
        response = self.client.post(
            self.url,
            data={'user': str(user.id), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_COUNTRY_CODE='YY',
        )
        assert response.status_code == 201

        assert AbuseReport.objects.filter(user_id=user.id).exists()
        report = AbuseReport.objects.get(user_id=user.id)
        self.check_report(report, 'Abuse Report for User %s' % user)
        assert report.country_code == 'YY'


class TestUserAbuseViewSetLoggedOut(UserAbuseViewSetTestBase, TestCase):
    def check_reporter(self, report):
        assert not report.reporter


class TestUserAbuseViewSetLoggedIn(UserAbuseViewSetTestBase, TestCase):
    def setUp(self):
        super().setUp()
        self.user = user_factory()
        self.client.login_api(self.user)

    def check_reporter(self, report):
        assert report.reporter == self.user

    def test_throttle_ip_for_authenticated_users(self):
        user = user_factory()
        self.client.login_api(user)
        target_user = user_factory()
        for x in range(20):
            response = self.client.post(
                self.url,
                data={'user': str(target_user.username), 'message': 'abuse!'},
                REMOTE_ADDR='123.45.67.89',
                HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
            )
            assert response.status_code == 201, x

        # Different user, same IP: should still be blocked (> 20 / day).
        new_user = user_factory()
        self.client.login_api(new_user)
        response = self.client.post(
            self.url,
            data={'user': str(target_user.username), 'message': 'abuse!'},
            REMOTE_ADDR='123.45.67.89',
            HTTP_X_FORWARDED_FOR=f'123.45.67.89, {get_random_ip()}',
        )
        assert response.status_code == 429


class TestAppeal(TestCase):
    def setUp(self):
        self.addon = addon_factory()
        self.abuse_report = AbuseReport.objects.create(
            reason=AbuseReport.REASONS.HATE_SPEECH,
            guid=self.addon.guid,
            created=self.days_ago(2),
        )
        self.cinder_report = CinderReport.objects.create(
            abuse_report=self.abuse_report,
            decision_id='my-decision-id',
            decision_action=CinderReport.DECISION_ACTIONS.AMO_APPROVE,
            decision_date=self.days_ago(1),
            created=self.abuse_report.created,
        )
        self.url = reverse(
            'abuse.appeal', kwargs={'decision_id': self.cinder_report.decision_id}
        )
        patcher = mock.patch('olympia.abuse.views.appeal_to_cinder')
        self.addCleanup(patcher.stop)
        self.appeal_mock = patcher.start()

    def test_no_decision_yet(self):
        self.cinder_report.update(
            decision_action=CinderReport.DECISION_ACTIONS.NO_DECISION
        )
        assert self.client.get(self.url).status_code == 404

    def test_no_such_decision(self):
        url = reverse('abuse.appeal', kwargs={'decision_id': '1234-5678-9000'})
        assert self.client.get(url).status_code == 404

    def test_appeal_approval_anonymous_report_with_no_email(self):
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_appeal_approval_anonymous_report_with_email(self):
        self.abuse_report.update(reporter_email='me@example.com')
        response = self.client.get(self.url)
        assert response.status_code == 200
        doc = pq(response.content)
        email_input = doc('#id_email')[0]
        assert email_input.type == 'email'
        assert email_input.label.text == 'Email address:'
        assert not doc('#appeal-thank-you')
        assert not doc('#id_reason')
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0

    def test_appeal_approval_anonymous_report_with_email_post_invalid(self):
        self.abuse_report.update(reporter_email='me@example.com')
        response = self.client.post(self.url, {'email': 'absolutelynotme@example.com'})
        assert response.status_code == 200
        doc = pq(response.content)
        email_input = doc('#id_email')[0]
        assert email_input.type == 'email'
        assert doc('ul.errorlist').text() == 'Invalid email provided.'
        assert not doc('#id_reason')
        assert not doc('#appeal-thank-you')
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0

    def test_appeal_approval_anonymous_report_with_email_post(self):
        self.abuse_report.update(reporter_email='me@example.com')
        response = self.client.post(self.url, {'email': 'me@example.com'})
        assert response.status_code == 200
        doc = pq(response.content)
        email_input = doc('#id_email')[0]
        assert email_input.type == 'hidden'
        assert doc('#id_reason')
        assert not doc('#appeal-thank-you')
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0

        response = self.client.post(
            self.url, {'email': 'me@example.com', 'reason': 'I dont like this'}
        )
        assert response.status_code == 200
        doc = pq(response.content)
        assert doc('#appeal-thank-you')
        assert not doc('#id_reason')
        assert not doc('#appeal-submit')
        assert self.appeal_mock.delay.call_count == 1
        assert self.appeal_mock.delay.call_args_list[0][0] == ()
        assert self.appeal_mock.delay.call_args_list[0][1] == {
            'appeal_text': 'I dont like this',
            'decision_id': self.cinder_report.decision_id,
            'user_id': None,
        }

    def test_appeal_approval_anonymous_report_with_email_post_cant_be_appealed(self):
        self.cinder_report.update(decision_date=self.days_ago(200))
        self.abuse_report.update(reporter_email='me@example.com')
        response = self.client.get(self.url)
        assert response.status_code == 200
        doc = pq(response.content)
        email_input = doc('#id_email')[0]
        assert email_input.type == 'email'
        assert not doc('#id_reason')
        assert not doc('#appeal-thank-you')
        # Before an email has been entered and checked, we don't reveal whether
        # the decision can be appealed.
        assert "This decision can't be appealed" not in doc.text()
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0

        response = self.client.post(self.url, {'email': 'me@example.com'})
        assert response.status_code == 200
        doc = pq(response.content)
        assert not doc('#id_email')
        assert not doc('#appeal-thank-you')
        assert not doc('#id_reason')
        assert not doc('#appeal-submit')
        assert "This decision can't be appealed" in doc.text()
        assert self.appeal_mock.call_count == 0

    def test_appeal_approval_logged_in_report_redirect_to_login(self):
        self.user = user_factory()
        self.abuse_report.update(reporter=self.user)
        response = self.client.get(self.url)
        self.assertLoginRedirects(response, self.url)

    def test_appeal_approval_logged_in_report_wrong_user(self):
        self.user = user_factory()
        self.abuse_report.update(reporter=self.user)
        self.user2 = user_factory()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_appeal_approval_loggued_in_user(self):
        self.user = user_factory()
        self.abuse_report.update(reporter=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        doc = pq(response.content)
        assert not doc('#id_email')
        assert not doc('#appeal-thank-you')
        assert doc('#id_reason')
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0

    def test_appeal_approval_logged_in_report_cant_be_appealed(self):
        self.cinder_report.update(decision_date=self.days_ago(200))
        self.user = user_factory()
        self.abuse_report.update(reporter=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        doc = pq(response.content)
        assert not doc('#id_email')
        assert not doc('#appeal-thank-you')
        assert not doc('#id_reason')
        assert not doc('#appeal-submit')
        assert "This decision can't be appealed" in doc.text()
        assert self.appeal_mock.call_count == 0

    def test_appeal_rejection_not_logged_in(self):
        self.cinder_report.update(
            decision_action=CinderReport.DECISION_ACTIONS.AMO_DISABLE_ADDON
        )
        response = self.client.get(self.url)
        self.assertLoginRedirects(response, self.url)

    def test_appeal_rejection_not_author(self):
        self.cinder_report.update(
            decision_action=CinderReport.DECISION_ACTIONS.AMO_DISABLE_ADDON
        )
        user = user_factory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_appeal_rejection_author(self):
        self.cinder_report.update(
            decision_action=CinderReport.DECISION_ACTIONS.AMO_DISABLE_ADDON
        )
        user = user_factory()
        self.addon.authors.add(user)
        self.client.force_login(user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        doc = pq(response.content)
        assert not doc('#id_email')
        assert not doc('#appeal-thank-you')
        assert doc('#id_reason')
        assert doc('#appeal-submit')

        response = self.client.post(
            self.url, {'email': 'me@example.com', 'reason': 'I dont like this'}
        )
        assert response.status_code == 200
        doc = pq(response.content)
        assert doc('#appeal-thank-you')
        assert not doc('#id_reason')
        assert not doc('#appeal-submit')
        assert self.appeal_mock.delay.call_count == 1
        assert self.appeal_mock.delay.call_args_list[0][0] == ()
        assert self.appeal_mock.delay.call_args_list[0][1] == {
            'appeal_text': 'I dont like this',
            'decision_id': self.cinder_report.decision_id,
            'user_id': user.pk,
        }

    def test_appeal_banned_user(self):
        self.cinder_report.update(
            decision_action=CinderReport.DECISION_ACTIONS.AMO_BAN_USER
        )
        self.abuse_report.update(guid=None, user=user_factory())
        response = self.client.post(self.url, {'email': self.abuse_report.user.email})
        assert response.status_code == 200
        doc = pq(response.content)
        email_input = doc('#id_email')[0]
        assert email_input.type == 'hidden'
        assert doc('#id_reason')
        assert not doc('#appeal-thank-you')
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0

        response = self.client.post(
            self.url,
            {'email': self.abuse_report.user.email, 'reason': 'I am not a bad guy'},
        )
        assert response.status_code == 200
        doc = pq(response.content)
        assert doc('#appeal-thank-you')
        assert not doc('#id_reason')
        assert not doc('#appeal-submit')
        assert self.appeal_mock.delay.call_count == 1
        assert self.appeal_mock.delay.call_args_list[0][0] == ()
        assert self.appeal_mock.delay.call_args_list[0][1] == {
            'appeal_text': 'I am not a bad guy',
            'decision_id': self.cinder_report.decision_id,
            'user_id': None,
        }

    def test_appeal_banned_user_wrong_email(self):
        self.cinder_report.update(
            decision_action=CinderReport.DECISION_ACTIONS.AMO_BAN_USER
        )
        self.abuse_report.update(guid=None, user=user_factory())
        response = self.client.post(self.url, {'email': 'me@example.com'})
        assert response.status_code == 200
        doc = pq(response.content)
        email_input = doc('#id_email')[0]
        assert email_input.type == 'email'
        assert doc('ul.errorlist').text() == 'Invalid email provided.'
        assert not doc('#id_reason')
        assert not doc('#appeal-thank-you')
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0

        response = self.client.post(
            self.url,
            {'email': 'me@example.com', 'reason': 'I am a bad guy'},
        )
        assert response.status_code == 200
        doc = pq(response.content)
        email_input = doc('#id_email')[0]
        assert email_input.type == 'email'
        assert doc('ul.errorlist').text() == 'Invalid email provided.'
        assert not doc('#id_reason')
        assert not doc('#appeal-thank-you')
        assert doc('#appeal-submit')
        assert self.appeal_mock.call_count == 0
