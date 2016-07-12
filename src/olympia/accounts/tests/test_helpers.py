import urlparse
from base64 import urlsafe_b64encode

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.test.utils import override_settings

import mock

from olympia.accounts import helpers
from olympia.amo.tests import create_switch

FXA_CONFIG = {
    'default': {
        'client_id': 'foo',
        'client_secret': 'bar',
        'something': 'hello, world!',
        'a_different_thing': 'howdy, world!',
    },
}
FXA_CONFIG_WITH_URLS = {
    'default': {
        'client_id': 'foo',
        'client_secret': 'bar',
        'oauth_host': 'https://accounts.firefox.com/oauth',
        'redirect_url': 'https://testserver/fxa',
        'scope': 'profile',
    },
}


@override_settings(FXA_CONFIG=FXA_CONFIG)
def test_fxa_config_anonymous():
    context = mock.MagicMock()
    context['request'].session = {'fxa_state': 'thestate!'}
    context['request'].user.is_authenticated.return_value = False
    assert helpers.fxa_config(context) == {
        'clientId': 'foo',
        'something': 'hello, world!',
        'state': 'thestate!',
        'aDifferentThing': 'howdy, world!',
    }


@override_settings(FXA_CONFIG=FXA_CONFIG)
def test_fxa_config_logged_in():
    context = mock.MagicMock()
    context['request'].session = {'fxa_state': 'thestate!'}
    context['request'].user.is_authenticated.return_value = True
    context['request'].user.email = 'me@mozilla.org'
    assert helpers.fxa_config(context) == {
        'clientId': 'foo',
        'something': 'hello, world!',
        'state': 'thestate!',
        'aDifferentThing': 'howdy, world!',
        'email': 'me@mozilla.org',
    }


@override_settings(FXA_CONFIG=FXA_CONFIG_WITH_URLS)
def test_default_fxa_login_url_with_state():
    path = '/en-US/addons/abp/?source=ddg'
    request = RequestFactory().get(path)
    request.session = {'fxa_state': 'myfxastate'}
    raw_url = helpers.default_fxa_login_url(request)
    url = urlparse.urlparse(raw_url)
    base = '{scheme}://{netloc}{path}'.format(
        scheme=url.scheme, netloc=url.netloc, path=url.path)
    assert base == 'https://accounts.firefox.com/oauth/authorization'
    query = urlparse.parse_qs(url.query)
    next_path = urlsafe_b64encode(path).rstrip('=')
    assert query == {
        'client_id': ['foo'],
        'redirect_url': ['https://testserver/fxa'],
        'scope': ['profile'],
        'state': ['myfxastate:{next_path}'.format(next_path=next_path)],
    }

@mock.patch(
    'olympia.accounts.helpers.default_fxa_login_url',
    lambda c: 'http://auth.ca')
@mock.patch('olympia.accounts.helpers.waffle.switch_is_active')
def test_login_link_migrated(switch_is_active):
    switch_is_active.return_value = True
    assert helpers.login_link({'request': mock.MagicMock()}) == 'http://auth.ca'
    switch_is_active.assert_called_with('fxa-migrated')

@mock.patch('olympia.accounts.helpers.waffle.switch_is_active')
def test_login_link_not_migrated(switch_is_active):
    request = RequestFactory().get('/en-US/foo')
    switch_is_active.return_value = False
    assert helpers.login_link({'request': request}) == (
        '{}?to=%2Fen-US%2Ffoo'.format(reverse('users.login')))
    switch_is_active.assert_called_with('fxa-migrated')

@mock.patch(
    'olympia.accounts.helpers.default_fxa_login_url',
    lambda c: 'http://auth.ca')
@mock.patch('olympia.accounts.helpers.waffle.switch_is_active')
def test_register_link_migrated(switch_is_active):
    switch_is_active.return_value = True
    assert helpers.register_link({'request': mock.MagicMock()}) == (
        'http://auth.ca')
    switch_is_active.assert_called_with('fxa-migrated')

@mock.patch('olympia.accounts.helpers.waffle.switch_is_active')
def test_register_link_not_migrated(switch_is_active):
    request = RequestFactory().get('/en-US/foo')
    switch_is_active.return_value = False
    assert helpers.register_link({'request': request}) == (
        '{}?to=%2Fen-US%2Ffoo'.format(reverse('users.register')))
    switch_is_active.assert_called_with('fxa-migrated')
