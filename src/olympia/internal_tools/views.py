import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from rest_framework.views import APIView, Response


from olympia.accounts.views import (
    add_api_token_to_response, update_user, with_user, ERROR_NO_USER,
    LoginStartBaseView)
from olympia.addons.views import AddonSearchView
from olympia.api.authentication import JSONWebTokenAuthentication
from olympia.api.permissions import AnyOf, GroupPermission
from olympia.search.filters import (
    InternalSearchParameterFilter, SearchQueryFilter, SortingFilter)

log = logging.getLogger('internal_tools')


class InternalAddonSearchView(AddonSearchView):
    # AddonSearchView disables auth classes so we need to add it back.
    authentication_classes = [JSONWebTokenAuthentication]

    # Similar to AddonSearchView but without the PublicContentFilter and with
    # InternalSearchParameterFilter instead of SearchParameterFilter to allow
    # searching by status.
    filter_backends = [
        SearchQueryFilter, InternalSearchParameterFilter, SortingFilter
    ]

    # Restricted to specific permissions.
    permission_classes = [AnyOf(GroupPermission('AdminTools', 'View'),
                                GroupPermission('ReviewerAdminTools', 'View'))]


class LoginStartView(LoginStartBaseView):
    FXA_CONFIG_NAME = 'internal'


class LoginView(APIView):

    @with_user(format='json', config='internal')
    def post(self, request, user, identity, next_path):
        if user is None:
            return Response({'error': ERROR_NO_USER}, status=422)
        else:
            update_user(user, identity)
            response = Response({'email': identity['email']})
            add_api_token_to_response(response, user, set_cookie=False)
            log.info('Logging in user {} from FxA'.format(user))
            return response

    def options(self, request):
        return Response()
