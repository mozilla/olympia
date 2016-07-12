import os
from base64 import urlsafe_b64encode
from urllib import urlencode

from django.conf import settings
from django.core import urlresolvers
from django.utils.http import is_safe_url

import jinja2
import waffle
from jingo import register

from olympia.amo.utils import urlparams


@register.function
@jinja2.contextfunction
def login_link(context):
    if waffle.switch_is_active('fxa-migrated'):
        return default_fxa_login_url(context['request'])
    else:
        return link_with_final_destination(
            context, urlresolvers.reverse('users.login'))


@register.function
@jinja2.contextfunction
def register_link(context):
    if waffle.switch_is_active('fxa-migrated'):
        return default_fxa_login_url(context['request'])
    else:
        return link_with_final_destination(
            context, urlresolvers.reverse('users.register'))


@register.function
@jinja2.contextfunction
def fxa_config(context):
    request = context['request']
    config = {camel_case(key): value
              for key, value in settings.FXA_CONFIG['default'].iteritems()
              if key != 'client_secret'}
    if request.user.is_authenticated():
        config['email'] = request.user.email
    request.session.setdefault('fxa_state', generate_fxa_state())
    config['state'] = request.session['fxa_state']
    return config


def link_with_final_destination(context, base):
    return urlparams(base, to=path_with_query(context['request']))


def path_with_query(request):
    next_path = request.path
    qs = request.GET.urlencode()
    if qs:
        return '{next_path}?{qs}'.format(next_path=next_path, qs=qs)
    else:
        return next_path


def fxa_login_url(config, state, next_path=None, action=None):
    if next_path and is_safe_url(next_path):
        state += ':' + urlsafe_b64encode(next_path).rstrip('=')
    query = {
        'client_id': config['client_id'],
        'redirect_url': config['redirect_url'],
        'scope': config['scope'],
        'state': state,
    }
    if action is not None:
        query['action'] = action
    return '{host}/authorization?{query}'.format(
        host=config['oauth_host'], query=urlencode(query))


def default_fxa_login_url(request):
    request.session.setdefault('fxa_state', generate_fxa_state())
    return fxa_login_url(
        config=settings.FXA_CONFIG['default'],
        state=request.session['fxa_state'],
        next_path=path_with_query(request))


def generate_fxa_state():
    return os.urandom(32).encode('hex')


def camel_case(snake):
    parts = snake.split('_')
    return parts[0] + ''.join(part.capitalize() for part in parts[1:])
