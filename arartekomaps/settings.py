# Django settings for arartekomaps project.

import os
from django.utils.translation import ugettext_lazy as _

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = ''
EMAIL_NOTIFICATION = ''

ADMINS = (
    ('Admin', 'admin@your_email.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'pos$
        'NAME': '',                      # Or path to database file$
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. N$
        'PORT': '',                      # Set to empty string for default. Not$

    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3
THOUSAND_SEPARATOR = '.'

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s

PAGE_LANGUAGES = (
  ('es', gettext_noop('Espanol')),
  ('eu', gettext_noop('Euskara')),
  ('en', gettext_noop('English')),
)

"""
PAGE_LANGUAGES = (
  ('es', 'Espanol'),
  ('eu', 'Euskara'),
)
"""

LANGUAGES = list(PAGE_LANGUAGES)

TRANSMETA_LANGUAGES = LANGUAGES


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/home/csmant/django/ararteko/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/csmant/django/ararteko/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',    
)

ROOT_URLCONF = 'arartekomaps.urls'


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/templates' % BASE_DIR,

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages'
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.comments',
    'arartekomaps',
    'arartekomaps.places',
    'arartekomaps.locations',
    'arartekomaps.categories',
    'arartekomaps.mycomment',
    'cssocialprofile',
    'social_auth',
    'registration',
    'photologue',
    'pages',
    'gunicorn',
    'piston',
    'modeltranslation',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

#SMTP CONFIG
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = ''

HOST = ''

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    #'social_auth.backends.google.GoogleBackend',
    #'social_auth.backends.yahoo.YahooBackend',
    #'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'social_auth.backends.OpenIDBackend',
    #'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    'django.contrib.auth.backends.ModelBackend',
)

#Login
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/u/'
LOGOUT_URL = '/u/logout'

AUTH_PROFILE_MODULE = 'cssocialprofile.CSSocialProfile'

#Dajngo-registration settings
ACCOUNT_ACTIVATION_DAYS = 5

#Twitter API
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
REQUEST_TOKEN = ''
ACCESS_TOKEN = ''
AUTHORIZE_URL = ''

#Facebook API

FACEBOOK_APP_ID = ''
FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''

PAGE_DEFAULT_TEMPLATE = 'pages/index.html'

MODELTRANSLATION_DEFAULT_LANGUAGE = 'es'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('es', 'eu')

IMPORT_FILES_FOLDER = '/var/csmant/ararimport'


USE_X_FORWARDED_HOST = True

try:
    from server_settings import *
except:
    pass

try:
    from local_settings import *
except:
    pass
