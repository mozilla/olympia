import re
from collections import namedtuple

from django.utils.translation import gettext_lazy as _


# Add-on and File statuses.
STATUS_NULL = 0  # No review type chosen yet, add-on is incomplete.
STATUS_AWAITING_REVIEW = 1  # File waiting for review.
_STATUS_PENDING = 2  # Deprecated. Was Personas waiting for review.
STATUS_NOMINATED = 3  # Waiting for review.
STATUS_APPROVED = 4  # Approved.
STATUS_DISABLED = 5  # Rejected (single files) or disabled by Mozilla (addons).
_STATUS_LISTED = 6  # Deprecated. See bug 616242
_STATUS_BETA = 7  # Deprecated, see addons-server/issues/7163
_STATUS_LITE = 8  # Deprecated, preliminary reviewed.
_STATUS_LITE_AND_NOMINATED = 9  # Deprecated, prelim & waiting for full review.
STATUS_DELETED = 11  # Add-on has been deleted.
_STATUS_REJECTED = 12  # Deprecated. Applied only to rejected personas.
_STATUS_REVIEW_PENDING = 14  # Deprecated. Was personas, needing further action

STATUS_CHOICES_ADDON = {
    STATUS_NULL: _('Incomplete'),
    STATUS_NOMINATED: _('Awaiting Review'),
    STATUS_APPROVED: _('Approved'),
    STATUS_DISABLED: _('Disabled by Mozilla'),
    STATUS_DELETED: _('Deleted'),
}

STATUS_CHOICES_FILE = {
    STATUS_AWAITING_REVIEW: _('Awaiting Review'),
    STATUS_APPROVED: _('Approved'),
    STATUS_DISABLED: _('Disabled by Mozilla'),
}

# We need to expose nice values that aren't localisable.
STATUS_CHOICES_API = {
    STATUS_NULL: 'incomplete',
    STATUS_AWAITING_REVIEW: 'unreviewed',
    STATUS_NOMINATED: 'nominated',
    STATUS_APPROVED: 'public',
    STATUS_DISABLED: 'disabled',
    STATUS_DELETED: 'deleted',
}

STATUS_CHOICES_API_LOOKUP = {
    'incomplete': STATUS_NULL,
    'unreviewed': STATUS_AWAITING_REVIEW,
    'nominated': STATUS_NOMINATED,
    'public': STATUS_APPROVED,
    'disabled': STATUS_DISABLED,
    'deleted': STATUS_DELETED,
}

APPROVED_STATUSES = (STATUS_APPROVED,)
UNREVIEWED_FILE_STATUSES = (STATUS_AWAITING_REVIEW,)
VALID_ADDON_STATUSES = (STATUS_NOMINATED, STATUS_APPROVED)
VALID_FILE_STATUSES = (STATUS_AWAITING_REVIEW, STATUS_APPROVED)

# Version channels
CHANNEL_UNLISTED = 1
CHANNEL_LISTED = 2

CHANNEL_CHOICES = (
    (CHANNEL_UNLISTED, _('Unlisted')),
    (CHANNEL_LISTED, _('Listed')),
)

CHANNEL_CHOICES_API = {
    CHANNEL_UNLISTED: 'unlisted',
    CHANNEL_LISTED: 'listed',
}

CHANNEL_CHOICES_LOOKUP = {
    'unlisted': CHANNEL_UNLISTED,
    'listed': CHANNEL_LISTED,
}

UPLOAD_SOURCE_DEVHUB = 1
UPLOAD_SOURCE_SIGNING_API = 2
UPLOAD_SOURCE_ADDON_API = 3
UPLOAD_SOURCE_GENERATED = 4
UPLOAD_SOURCE_CHOICES = (
    (UPLOAD_SOURCE_DEVHUB, _('Developer Hub')),
    (UPLOAD_SOURCE_SIGNING_API, _('Signing API')),
    (UPLOAD_SOURCE_ADDON_API, _('Add-on API')),
    (UPLOAD_SOURCE_GENERATED, _('Automatically generated by AMO')),
)

# Add-on author roles.
AUTHOR_ROLE_DEV = 4
AUTHOR_ROLE_OWNER = 5
AUTHOR_ROLE_DELETED = 6

AUTHOR_CHOICES = (
    (AUTHOR_ROLE_OWNER, _('Owner')),
    (AUTHOR_ROLE_DEV, _('Developer')),
)

AUTHOR_CHOICES_API = {
    AUTHOR_ROLE_OWNER: 'owner',
    AUTHOR_ROLE_DEV: 'developer',
}

AUTHOR_CHOICES_UNFILTERED = AUTHOR_CHOICES + ((AUTHOR_ROLE_DELETED, _('(Deleted)')),)

# Addon types
ADDON_ANY = 0
ADDON_EXTENSION = 1
_ADDON_THEME = 2  # Obsolete.  XUL Theme.
ADDON_DICT = 3
_ADDON_SEARCH = 4  # Obsolete.  Opensearch.
ADDON_LPAPP = 5
_ADDON_LPADDON = 6  # Obsolete.  A langpack for a specific extension.
_ADDON_PLUGIN = 7  # Obsolete.  Binary plugin, e.g. Flash.
ADDON_API = 8  # not actually a type but used to identify extensions + themes
_ADDON_PERSONA = 9  # Obsolete.  Aka Lightweight Themes.
ADDON_STATICTHEME = 10
_ADDON_WEBAPP = 11  # Obsolete.  Marketplace cruft.
_ADDON_SITE_PERMISSION = 12  # Obsolete.  Never used in production.

# Addon type groupings

GROUP_TYPE_ADDON = (ADDON_EXTENSION, ADDON_DICT, ADDON_LPAPP)
GROUP_TYPE_THEME = (ADDON_STATICTHEME,)

# Singular
ADDON_TYPE = {
    ADDON_EXTENSION: _('Extension'),
    _ADDON_THEME: _('Deprecated Complete Theme'),
    ADDON_DICT: _('Dictionary'),
    _ADDON_SEARCH: _('Deprecated Search Engine'),
    ADDON_LPAPP: _('Language Pack'),
    _ADDON_LPADDON: _('Deprecated Language Pack (Add-on)'),
    _ADDON_PLUGIN: _('Deprecated Plugin'),
    _ADDON_PERSONA: _('Deprecated LWT'),
    ADDON_STATICTHEME: _('Theme'),
    _ADDON_SITE_PERMISSION: _('Deprecated Site Permission'),
}

# Plural
ADDON_TYPES = {
    ADDON_EXTENSION: _('Extensions'),
    _ADDON_THEME: _('Deprecated Complete Themes'),
    ADDON_DICT: _('Dictionaries'),
    _ADDON_SEARCH: _('Deprecated Search Tools'),
    ADDON_LPAPP: _('Language Packs'),
    _ADDON_LPADDON: _('Deprecated Language Packs (Add-on)'),
    _ADDON_PLUGIN: _('Deprecated Plugins'),
    _ADDON_PERSONA: _('Deprecated LWTs'),
    ADDON_STATICTHEME: _('Themes'),
    _ADDON_SITE_PERMISSION: _('Deprecated Site Permissions'),
}

# Searchable Add-on Types
ADDON_SEARCH_TYPES = (
    ADDON_ANY,
    ADDON_EXTENSION,
    _ADDON_THEME,
    ADDON_DICT,
    _ADDON_SEARCH,
    ADDON_LPAPP,
    _ADDON_PERSONA,
    ADDON_STATICTHEME,
)

# We use these slugs in browse page urls.
ADDON_SLUGS = {
    ADDON_EXTENSION: 'extensions',
    ADDON_DICT: 'language-tools',
    ADDON_LPAPP: 'language-tools',
    _ADDON_SEARCH: 'search-tools',
    ADDON_STATICTHEME: 'themes',
}

# A slug to ID map for the search API. Included are all ADDON_TYPES that are
# found in ADDON_SEARCH_TYPES.
ADDON_SEARCH_SLUGS = {
    'any': ADDON_ANY,
    'extension': ADDON_EXTENSION,
    'theme': _ADDON_THEME,
    'dictionary': ADDON_DICT,
    'search': _ADDON_SEARCH,
    'language': ADDON_LPAPP,
    'persona': _ADDON_PERSONA,
    'statictheme': ADDON_STATICTHEME,
}

ADDON_TYPE_CHOICES_API = {
    ADDON_EXTENSION: 'extension',
    _ADDON_THEME: 'theme',
    ADDON_DICT: 'dictionary',
    _ADDON_SEARCH: 'search',
    ADDON_LPAPP: 'language',
    _ADDON_PERSONA: 'persona',
    ADDON_STATICTHEME: 'statictheme',
}

ADDON_TYPES_WITH_STATS = (
    ADDON_EXTENSION,
    ADDON_STATICTHEME,
    ADDON_DICT,
    ADDON_LPAPP,
)

# Edit addon information
MAX_TAGS = 10
MAX_CATEGORIES = 3
CONTRIBUTE_UTM_PARAMS = {
    'utm_content': 'product-page-contribute',
    'utm_medium': 'referral',
    'utm_source': 'addons.mozilla.org',
}
VALID_CONTRIBUTION_DOMAINS = (
    'buymeacoffee.com',
    'donate.mozilla.org',
    'flattr.com',
    'github.com',
    'ko-fi.com',
    'liberapay.com',
    'www.micropayment.de',
    'opencollective.com',
    'www.patreon.com',
    'www.paypal.com',
    'paypal.me',
)

# Icon upload sizes
ADDON_ICON_SIZES = (32, 64, 128)
ADDON_ICON_FORMAT = 'png'

_dimensions = namedtuple('SizeTuple', 'width height')
# Preview upload sizes - see mozilla/addons-server#9487 & #16717 for background.
ADDON_PREVIEW_SIZES = {
    'thumbnail': _dimensions(533, 400),
    'min': _dimensions(1000, 750),
    'full': _dimensions(2400, 1800),
    'image_format': 'png',
    'thumbnail_format': 'jpg',
}

# Static theme preview renderings, with different dimensions
THEME_PREVIEW_RENDERINGS = {
    'firefox': {
        'thumbnail': _dimensions(473, 64),
        'full': _dimensions(680, 92),
        'position': 0,
        'image_format': 'png',
        'thumbnail_format': 'png',
    },
    'amo': {
        'thumbnail': _dimensions(720, 92),
        'full': _dimensions(720, 92),
        'position': 2,
        'image_format': 'svg',
        'thumbnail_format': 'jpg',
    },
}
THEME_FRAME_COLOR_DEFAULT = 'rgba(229,230,232,1)'
THEME_PREVIEW_TOOLBAR_HEIGHT = 92  # The template toolbar is this height.

# Accepted image extensions and MIME-types
THEME_BACKGROUND_EXTS = ('.jpg', '.jpeg', '.png', '.apng', '.svg', '.gif')
IMG_TYPES = ('image/png', 'image/jpeg')
VIDEO_TYPES = ('video/webm',)

# The string concatinating all accepted image MIME-types with '|'
SUPPORTED_IMAGE_TYPES = '|'.join(IMG_TYPES)

# Acceptable Add-on file extensions.
# This is being used by `parse_addon` so please make sure we don't have
# to touch add-ons before removing anything from this list.
VALID_ADDON_FILE_EXTENSIONS = ('.crx', '.xpi', '.zip')

# These types don't allow developer defined compatibility.
NO_COMPAT_CHANGES = (ADDON_DICT,)

# Validation.

# A skeleton set of passing validation results.
VALIDATOR_SKELETON_RESULTS = {
    'errors': 0,
    'warnings': 0,
    'notices': 0,
    'success': True,
    'compatibility_summary': {'notices': 0, 'errors': 0, 'warnings': 0},
    'metadata': {
        'listed': True,
    },
    'messages': [],
    'message_tree': {},
    'ending_tier': 5,
}

# A skeleton set of validation results for a system error.
VALIDATOR_SKELETON_EXCEPTION_WEBEXT = {
    'errors': 1,
    'warnings': 0,
    'notices': 0,
    'success': False,
    'compatibility_summary': {'notices': 0, 'errors': 0, 'warnings': 0},
    'metadata': {'listed': True},
    'messages': [
        {
            'id': ['validator', 'unexpected_exception'],
            'message': "Sorry, we couldn't load your WebExtension.",
            'description': [
                'Validation was unable to complete successfully due to an '
                'unexpected error.',
                'Check https://developer.mozilla.org/en-US/Add-ons/WebExtensions '
                'to ensure your webextension is valid or file a bug at '
                'http://bit.ly/1POrYYU',
            ],
            'type': 'error',
            'fatal': True,
            'tier': 1,
            'for_appversions': None,
            'uid': '35432f419340461897aa8362398339c4',
        }
    ],
    'message_tree': {},
    'ending_tier': 5,
}

VERSION_SEARCH = re.compile(r'\.(\d+)$')

# For use in urls.
ADDON_ID = r"""(?P<addon_id>[^/<>"']+)"""
ADDON_UUID = r'(?P<uuid>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})'

# Default strict_min_version and strict_max_version for WebExtensions
# We're signing with SHA256 nowadays, which is only supported in 58.0 or higher
DEFAULT_WEBEXT_MIN_VERSION = '58.0'
DEFAULT_WEBEXT_MAX_VERSION = '*'

# Android only started to support WebExtensions with version 48
DEFAULT_WEBEXT_MIN_VERSION_ANDROID = '58.0'

# The version of desktop Firefox that first supported static themes.
DEFAULT_STATIC_THEME_MIN_VERSION_FIREFOX = '58.0'

# The version of Firefox that first supported webext dictionaries.
# Dicts are not compatible with Firefox for Android, only desktop is relevant.
DEFAULT_WEBEXT_DICT_MIN_VERSION_FIREFOX = '61.0'

# The version of Firefox that first supported manifest version 3 (MV3)
DEFAULT_WEBEXT_MIN_VERSION_MV3_FIREFOX = '109.0a1'

# We don't know if the Android min version will be different, but assume it might be.
DEFAULT_WEBEXT_MIN_VERSION_MV3_ANDROID = DEFAULT_WEBEXT_MIN_VERSION_MV3_FIREFOX

# The version of Firefox for Android that first supported `gecko_android` key.
DEFAULT_WEBEXT_MIN_VERSION_GECKO_ANDROID = '113.0'

# First version we consider as "Fenix".
MIN_VERSION_FENIX = '79.0a1'

# Last version we consider as "Fennec"
MAX_VERSION_FENNEC = '68.*'

# The minimum version of Fenix where extensions are all available.
MIN_VERSION_FENIX_GENERAL_AVAILABILITY = '120.0'

ADDON_GUID_PATTERN = re.compile(
    # Match {uuid} or something@host.tld ("something" being optional)
    # guids. Copied from mozilla-central XPIProvider.jsm.
    r'^(\{[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\}'
    r'|[a-z0-9-\._]*\@[a-z0-9-\._]+)$',
    re.IGNORECASE,
)

# Changes to this list need to be coordinated with the Operations team to make
# sure other systems like the privileged add-ons signing pipeline are in sync.
# Please reach out to them before making changes.
RESERVED_ADDON_GUIDS = (
    '@mozilla.com',
    '@mozilla.org',
    '@pioneer.mozilla.org',
    '@search.mozilla.org',
    '@shield.mozilla.com',
    '@shield.mozilla.org',
    '@mozillaonline.com',
    '@mozillafoundation.org',
    '@rally.mozilla.org',
    # A temporary special case for aboutsync, which has a "legacy" ID.
    'aboutsync@mhammond.github.com',
    # Temporary add-ons as defined in Firefox. Should not be submitted to AMO.
    '@temporary-addon',
    # Android Components/Fenix built-in extensions.
    '@mozac.org',
    # Test privileged add-ons for mozilla-central.
    '@tests.mozilla.org',
)

MOZILLA_TRADEMARK_SYMBOLS = ('mozilla', 'firefox')

# If you add/remove any sources, update the docs: /api/download_sources.html
# Note there are some additional sources here for historical/backwards compat.
DOWNLOAD_SOURCES_FULL = (
    'addondetail',
    'addon-detail-version',
    'api',
    'category',
    'collection',
    'creatured',
    'developers',
    'discovery-dependencies',
    'discovery-upsell',
    'discovery-video',
    'email',
    'find-replacement',
    'fxcustomization',
    'fxfirstrun',
    'fxwhatsnew',
    'homepagebrowse',
    'homepagepromo',
    'installservice',
    'mostshared',
    'oftenusedwith',
    'prerelease-banner',
    'recommended',
    'rockyourfirefox',
    'search',
    'sharingapi',
    'similarcollections',
    'ss',
    'userprofile',
    'version-history',
    'co-hc-sidebar',
    'co-dp-sidebar',
    'cb-hc-featured',
    'cb-dl-featured',
    'cb-hc-toprated',
    'cb-dl-toprated',
    'cb-hc-mostpopular',
    'cb-dl-mostpopular',
    'cb-hc-recentlyadded',
    'cb-dl-recentlyadded',
    'hp-btn-promo',
    'hp-dl-promo',
    'hp-hc-featured',
    'hp-dl-featured',
    'hp-hc-upandcoming',
    'hp-dl-upandcoming',
    'hp-hc-mostpopular',
    'hp-dl-mostpopular',
    'hp-contest-winners',
    'dp-hc-oftenusedwith',
    'dp-dl-oftenusedwith',
    'dp-hc-othersby',
    'dp-dl-othersby',
    'dp-btn-primary',
    'dp-btn-version',
    'dp-btn-devchannel',
    'dp-hc-dependencies',
    'dp-dl-dependencies',
    'dp-hc-upsell',
    'dp-dl-upsell',
)

DOWNLOAD_SOURCES_PREFIX = ('external-', 'mozcom-', 'discovery-', 'cb-btn-', 'cb-dl-')

# Regexp for Firefox client IDs passed to our APIs, just to avoid sending
# garbage to underlying services.
VALID_CLIENT_ID = re.compile('^[a-zA-Z0-9]{64}$')

APPVERSIONS_ORIGINATED_FROM_UNKNOWN = 0
APPVERSIONS_ORIGINATED_FROM_AUTOMATIC = 1
APPVERSIONS_ORIGINATED_FROM_DEVELOPER = 2
APPVERSIONS_ORIGINATED_FROM_MANIFEST = 3
APPVERSIONS_ORIGINATED_FROM_MANIFEST_GECKO_ANDROID = 4
APPVERSIONS_ORIGINATED_FROM_MIGRATION = 5
