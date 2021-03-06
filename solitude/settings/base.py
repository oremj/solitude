import logging.handlers
import os

import cef
import dj_database_url

from funfactory.settings_base import *

ALLOWED_HOSTS = []
PROJECT_MODULE = 'solitude'
MINIFY_BUNDLES = {}

# Defines the views served for root URLs.
ROOT_URLCONF = '%s.urls' % PROJECT_MODULE

INSTALLED_APPS = (
    'aesfield',
    'funfactory',
    'django_extensions',
    'django_nose',
    'django_statsd',
    'solitude',
    'rest_framework',
    'django_filters'
)
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config()
    }
    if 'mysql' in DATABASES['default']['ENGINE']:
        opt = DATABASES['default'].get('OPTIONS', {})
        opt['init_command'] = 'SET storage_engine=InnoDB'
        opt['charset'] = 'utf8'
        opt['use_unicode'] = True
        DATABASES['default']['OPTIONS'] = opt
    DATABASES['default']['TEST_CHARSET'] = 'utf8'
    DATABASES['default']['TEST_COLLATION'] = 'utf8_general_ci'

else:
    DATABASES = {}

if os.environ.get('MEMCACHE_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': os.getenv('MEMCACHE_URL'),
        }
    }

LOCALE_PATHS = ()
USE_I18N = False
USE_L10N = False
USE_ETAGS = True

SOLITUDE_PROXY = os.environ.get('SOLITUDE_PROXY', 'disabled') == 'enabled'
if SOLITUDE_PROXY:
    # The proxy runs with no database access. And just a couple of libraries.
    INSTALLED_APPS += (
        'lib.proxy',
    )
else:
    # If this is the full solitude instance add in the rest.
    INSTALLED_APPS += (
        'lib.buyers',
        'lib.sellers',
        'lib.transactions',
        'lib.bango',
    )

TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

# Remove traces of jinja and jingo from solitude.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
JINJA_CONFIG = lambda: ''

if not SOLITUDE_PROXY:
    MIDDLEWARE_CLASSES = (
        'solitude.middleware.LoggerMiddleware',
        'django.middleware.transaction.TransactionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django_statsd.middleware.GraphiteMiddleware',
        'django_statsd.middleware.TastyPieRequestTimingMiddleware',
        'django_paranoia.middleware.Middleware'
    )
else:
    MIDDLEWARE_CLASSES = (
        'solitude.middleware.LoggerMiddleware',
        'django_statsd.middleware.GraphiteMiddleware',
    )

SESSION_COOKIE_SECURE = True

STATSD_CLIENT = 'django_statsd.clients.normal'

# PayPal values.
PAYPAL_APP_ID = ''
PAYPAL_AUTH = {'USER': '', 'PASSWORD': '', 'SIGNATURE': ''}
PAYPAL_CHAINS = ()
PAYPAL_CERT = None
PAYPAL_LIMIT_PREAPPROVAL = True
PAYPAL_URL_WHITELIST = ()
PAYPAL_USE_SANDBOX = True
PAYPAL_PROXY = ''
PAYPAL_MOCK = False

# Access the cleansed settings values.
CLEANSED_SETTINGS_ACCESS = False
# The status object for tastypie services.
SERVICES_STATUS_MODULE = 'lib.services.resources'


base_fmt = ('%(name)s:%(levelname)s %(message)s '
            ':%(pathname)s:%(lineno)s')
error_fmt = ('%(name)s:%(levelname)s %(request_path)s %(message)s '
             ':%(pathname)s:%(lineno)s')

LOGGING = {
    'version': 1,
    'filters': {},
    'formatters': {
        'solitude': {
            '()': 'solitude.logger.SolitudeFormatter',
            'format':
                '%(name)s:%(levelname)s '
                '%(OAUTH_KEY)s:%(TRANSACTION_ID)s '
                '%(message)s :%(pathname)s:%(lineno)s'
        },
        'cef': {
            '()': cef.SysLogFormatter,
            'datefmt': '%H:%M:%s',
        }
    },
    'handlers': {
        'unicodesyslog': {
            '()': 'mozilla_logger.log.UnicodeHandler',
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL7,
            'formatter': 'solitude',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            '()': logging.StreamHandler,
            'formatter': 'solitude',
        },
        'cef_syslog': {
            '()': logging.handlers.SysLogHandler,
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL4,
            'formatter': 'cef',
        },

    },
    'loggers': {
        '': {
            'handlers': ['unicodesyslog', 'sentry'],
            'level': 'INFO',
            'propagate': True
        },
        's.services': {
            'handlers': ['unicodesyslog'],
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['unicodesyslog', 'sentry'],
            'level': 'INFO',
            'propagate': True
        },
        'requests.packages.urllib3.connectionpool': {
            'level': 'WARNING',
            'propagate': True
        },
        'suds': {
            # This is very verbose and setting it to DEBUG may
            # cause problems on jenkins because the logging within suds
            # actually causes errors.
            'level': 'ERROR',
            'propagate': True
        },
        'boto': {
            'level': 'ERROR',
            'propagate': True
        },
        'cef': {
            'handlers': ['cef_syslog']
        }
    }
}
LOGGING_CONFIG = 'django.utils.log.dictConfig'

# These are the AES encryption keys for different fields.
AES_KEYS = {
    'buyerpaypal:key': '',
    'sellerpaypal:id': '',
    'sellerpaypal:token': '',
    'sellerpaypal:secret': '',
    'sellerproduct:secret': '',
}

# Playdoh ships with sha512 password hashing by default. Bcrypt+HMAC is safer,
# so it is recommended. Please read
# <https://github.com/fwenzel/django-sha2#readme>, uncomment the bcrypt hasher
# and pick a secret HMAC key for your application.
BASE_PASSWORD_HASHERS = (
    'django_sha2.hashers.BcryptHMACCombinedPasswordVerifier',
    'django_sha2.hashers.SHA512PasswordHasher',
    'django_sha2.hashers.SHA256PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)

DUMP_REQUESTS = False

# If this flag is set, any communication will require OAuth signing of the
# request. Without this, OAuth is optional. This should be True for production.
REQUIRE_OAUTH = False

# A mapping of the keys and secrets that will be used to sign OAuth
# for any server talking to this server.
CLIENT_OAUTH_KEYS = {}

# Bango API settings.
# These are the credentials for calling Bango.
BANGO_AUTH = {'USER': 'Mozilla', 'PASSWORD': ''}

# The Bango API environment. This value must be an existing subdirectory
# under lib/bango/wsdl.
BANGO_ENV = 'test'
BANGO_MOCK = False
BANGO_PROXY = ''

# Set this to a string if you'd like to insert data into the vendor
# and company name when a package is created.
BANGO_INSERT_STAGE = ''

# Notification end points use basic auth.
# These are the credentials for Bango calling us.
BANGO_BASIC_AUTH = {'USER': '', 'PASSWORD': ''}

# The URL that Bango will send notifications too. If this is not set, the
# notification URL will not be set.
BANGO_NOTIFICATION_URL = ''

# Time in seconds that a transaction expires. If you try to complete a
# transaction after this time, it will fail.
TRANSACTION_EXPIRY = 60 * 30

# Time in seconds after a transaction is created that it becomes locked.
# After that time, no changes can be made to a transaction.
TRANSACTION_LOCKDOWN = 60 * 60 * 24

# Paranoia levels.
DJANGO_PARANOIA_REPORTERS = [
    'django_paranoia.reporters.log',
    'django_paranoia.reporters.cef_'
]

# The number of PIN failures before we lock them out.
PIN_FAILURES = 5
# The amount of time before you can try it again in seconds.
PIN_FAILURE_LENGTH = 300

# Ensure that sensitive data in the JSON is filtered out.
RAVEN_CONFIG = {
    'processors': ('solitude.processor.JSONProcessor',),
}
# Sensitive keys.
SENSITIVE_DATA_KEYS = ['bankAccountNumber', 'pin', 'secret']

# Set this for OAuth.
SITE_URL = ''

# Fake out refunds, set this to True for test until bug 845332 is resolved.
# Turning this on, just fakes out the Bango backend completely and never
# really refunds anything.
#
# This is different from manual refund which is to force a refund through
# if Bango use the manual refund flow.
BANGO_FAKE_REFUNDS = False

# When True, send product icon URLs to Bango in the billing config task.
BANGO_ICON_URLS = True

# When True, send MOZ_USER_ID to Bango in the billing config task.
SEND_USER_ID_TO_BANGO = True

# Time in seconds after which a Bango API request will be aborted.
# We can deal with slow requests because we mostly use background tasks.
# The API can indeed be slow, see bug 883389.
BANGO_TIMEOUT = 30

# Time in days after which Bango statuses will be cleaned by the
# `clean_statuses` command.
BANGO_STATUSES_LIFETIME = 30

# When True, use the token check service to verify query string parameters.
CHECK_BANGO_TOKEN = True

REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'solitude.authentication.RestOAuthAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_SERIALIZER_CLASS':
        'solitude.paginator.CustomPaginationSerializer',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'limit'
}

# For uploading logs from the server.
S3_AUTH = {'key': '',
           'secret': ''}
S3_BUCKET = ''

# New Relic is configured here.
NEWRELIC_INI = None

# Here be all the zippy stuff.
ZIPPY_MOCK = False
# Override this to configure some zippy backends.
ZIPPY_CONFIGURATION = {}

# The URL for a solitude proxy to zippy.
ZIPPY_PROXY = ''

# Flip to the new billing configuration for Bango. This is temporary and once
# we are on the new config, we can probably remove it.
BANGO_BILLING_CONFIG_V2 = False

# Boku Settings
BOKU_API_DOMAIN = 'https://api2.boku.com'
BOKU_SECRET_KEY = ''
