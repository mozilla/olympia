import json
import tempfile
from unittest import mock

from django.conf import settings
from django.test.utils import override_settings

import responses

from olympia.amo.tests import TestCase
from olympia.lib.remote_settings import RemoteSettings


@override_settings(
    BLOCKLIST_REMOTE_SETTINGS_USERNAME='test_username',
    BLOCKLIST_REMOTE_SETTINGS_PASSWORD='test_password',
)
class TestRemoteSettings(TestCase):
    def test_setup_server_auth(self):
        server = RemoteSettings('foo', 'baa')
        responses.add(
            responses.GET,
            settings.REMOTE_SETTINGS_WRITER_URL,
            content_type='application/json',
            json={'user': {'id': ''}},
        )
        responses.add(
            responses.PUT,
            settings.REMOTE_SETTINGS_WRITER_URL + 'accounts/test_username',
            content_type='application/json',
            json={'data': {'password': 'test_password'}},
            status=201,
        )
        server.setup_test_server_auth()

        # If repeated then the account should exist the 2nd time
        responses.add(
            responses.GET,
            settings.REMOTE_SETTINGS_WRITER_URL,
            content_type='application/json',
            json={'user': {'id': 'account:test_username'}},
        )
        server.setup_test_server_auth()

    def test_setup_server_bucket(self):
        server = RemoteSettings('foo', 'baa')
        # if the server 403s on the bucket it's because it doesn't exist
        responses.add(
            responses.GET,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo',
            content_type='application/json',
            status=403,
        )
        responses.add(
            responses.PUT,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo',
            content_type='application/json',
        )
        # if the server 404s on the collection it's because it doesn't exist
        responses.add(
            responses.GET,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa',
            content_type='application/json',
            status=404,
        )
        responses.add(
            responses.PUT,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa',
            content_type='application/json',
            status=201,
        )
        server.setup_test_server_collection()

    def test_setup_server_collection(self):
        server = RemoteSettings('foo', 'baa')
        # But if the bucket exists then the collection should still be created
        responses.add(
            responses.GET,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo',
            content_type='application/json',
        )
        responses.add(
            responses.GET,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa',
            content_type='application/json',
            status=404,
        )
        responses.add(
            responses.PUT,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa',
            content_type='application/json',
            status=201,
        )
        server.setup_test_server_collection()

    @override_settings(REMOTE_SETTINGS_IS_TEST_SERVER=False)
    def test_setup_not_test_server(self):
        server = RemoteSettings('foo', 'baa')

        server.setup()  # will just return
        assert server._setup_done
        assert server.bucket == 'foo'

    @override_settings(REMOTE_SETTINGS_IS_TEST_SERVER=True)
    def test_setup(self):
        server = RemoteSettings('foo', 'baa')
        responses.add(
            responses.GET,
            settings.REMOTE_SETTINGS_WRITER_URL,
            content_type='application/json',
            json={'user': {'id': 'account:test_username'}},
        )
        bucket_url = settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo_test_username'
        responses.add(responses.GET, bucket_url, content_type='application/json')
        responses.add(
            responses.GET,
            bucket_url + '/collections/baa',
            content_type='application/json',
        )

        server.setup()
        assert server._setup_done
        assert server.bucket == 'foo_test_username'

        server.setup()  # a second time shouldn't make any requests

    def test_publish_record(self):
        server = RemoteSettings('foo', 'baa')
        server._setup_done = True
        assert not server._changes
        responses.add(
            responses.POST,
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa/records',
            content_type='application/json',
            json={'data': {'id': 'new!'}},
        )

        record = server.publish_record({'something': 'somevalue'})
        assert server._changes
        assert record == {'id': 'new!'}

        url = (
            settings.REMOTE_SETTINGS_WRITER_URL
            + 'buckets/foo/collections/baa/records/an-id'
        )
        responses.add(
            responses.PUT,
            url,
            content_type='application/json',
            json={'data': {'id': 'updated'}},
        )

        record = server.publish_record({'something': 'somevalue'}, 'an-id')
        assert record == {'id': 'updated'}

    @mock.patch('olympia.lib.remote_settings.uuid')
    def test_publish_attachment(self, uuidmock):
        uuidmock.uuid4.return_value = 1234567890
        server = RemoteSettings('foo', 'baa')
        server._setup_done = True
        assert not server._changes
        url = (
            settings.REMOTE_SETTINGS_WRITER_URL
            + 'buckets/foo/collections/baa/records/1234567890/attachment'
        )
        responses.add(responses.POST, url, json={'data': {'id': '1234567890'}})

        with tempfile.TemporaryFile() as attachment:
            record = server.publish_attachment(
                {'something': 'somevalue'}, ('file', attachment)
            )
        assert server._changes
        assert record == {'id': '1234567890'}

        url = (
            settings.REMOTE_SETTINGS_WRITER_URL
            + 'buckets/foo/collections/baa/records/an-id/attachment'
        )
        responses.add(responses.POST, url, json={'data': {'id': 'an-id'}})

        with tempfile.TemporaryFile() as attachment:
            record = server.publish_attachment(
                {'something': 'somevalue'}, ('otherfile', attachment), 'an-id'
            )
        assert record == {'id': 'an-id'}

    def test_delete_record(self):
        server = RemoteSettings('foo', 'baa')
        server._setup_done = True
        assert not server._changes
        url = (
            settings.REMOTE_SETTINGS_WRITER_URL
            + 'buckets/foo/collections/baa/records/an-id'
        )
        responses.add(responses.DELETE, url, content_type='application/json')

        server.delete_record('an-id')
        assert server._changes

    def test_delete_all_records(self):
        server = RemoteSettings('foo', 'baa')
        server._setup_done = True
        assert not server._changes
        url = (
            settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa/records'
        )
        responses.add(responses.DELETE, url, content_type='application/json')

        server.delete_all_records()
        assert server._changes

    def test_complete_session(self):
        server = RemoteSettings('foo', 'baa')
        server._setup_done = True
        # should return because nothing to signoff
        server.complete_session()

        server._changes = True
        url = settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa'
        responses.add(responses.PATCH, url, content_type='application/json')
        server.complete_session()
        assert not server._changes
        assert (
            responses.calls[0].request.body
            == json.dumps({'data': {'status': 'to-review'}}).encode()
        )

    def test_complete_session_no_signoff(self):
        server = RemoteSettings('foo', 'baa', sign_off_needed=False)
        server._setup_done = True
        # should return because nothing to signoff
        server.complete_session()

        server._changes = True
        url = settings.REMOTE_SETTINGS_WRITER_URL + 'buckets/foo/collections/baa'
        responses.add(responses.PATCH, url, content_type='application/json')
        server.complete_session()
        assert not server._changes
        assert (
            responses.calls[0].request.body
            == json.dumps({'data': {'status': 'to-sign'}}).encode()
        )
