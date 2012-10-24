# Crichton, Admirable Source Configuration Management
# Copyright 2012 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
# Django settings for crichtonweb project.
#### PRODUCTION SETTINGS ####

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Admin', 'myadmin@nobody.com),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'crichton',                      # Or path to database file if using sqlite3.
        'USER': 'crichton',                      # Not used with sqlite3.
        'PASSWORD': 'ronnocnhoj',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

CACHE_BACKEND = "locmem://"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd}oFpZ6H\@a3iGLt/[6ZvV.sMMeVtZ0'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#
#    BBCRemoteUserMiddleware subclasses 'django.contrib.auth.middleware.RemoteUserMiddleware'
    'crichtonweb.frontend.bbc_remote_user_middleware.BBCRemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'audit_log.middleware.UserLoggingMiddleware'
)

ROOT_URLCONF = 'crichtonweb.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

API_EXPOSED_APPS = (
    'issue',
    'prodmgmt',
    'package',
    'ci',
    'system',
    'release',
    'deployment',
    'requirement', # Not yet used
    'frontend',
    'jirarpc',
)

INSTALLED_APPS = API_EXPOSED_APPS + (
    'admin',
    'api',
    'core',
    'jirarpc',
    'ajax_select',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    
    'south',
)

AUTH_PROFILE_MODULE = "api.person"

# BBCRemoteUserBackend subclasses django.contrib.auth.backends.RemoteUserBackend
AUTHENTICATION_BACKENDS = (
    'frontend.bbc_remote_user_backend.BBCRemoteUserBackend',
)

# AUTH_CONFIG is read and applied by the applyauthconfig.py script
# Note that this config is not necessarily exhaustive -- permissions
# that exist already are never removed when this config is applied
AUTH_CONFIG = {
    "groups": [
        "Users",
        "Operations"
    ],
    "superusers": [
        {
            "username":   "Dave.van.Zijl",
            "email":      "Dave.van.Zijl@domain.local",
            "first_name": "Dave",
            "last_name":  "van Zijl",
        },
        {
            "username":   "Leo.Simons",
            "email":      "Leo.Simons@domain.local",
            "first_name": "Leo",
            "last_name":  "Simons",
        },
        {
            "username":   "Rachel.Willmer",
            "email":      "Rachel.Willmer@domain.local",
            "first_name": "Rachel",
            "last_name":  "Willmer",
        },
        {
            "username":   "Simon.Lucy",
            "email":      "Simon.Lucy@domain.local",
            "first_name": "Simon",
            "last_name":  "Lucy",
        },
    ],
    "group_permissions": [
        {
            "group": "Users",
            "grants": [
                {
                    "actions": ["add", "change", "delete"], 
                    "models": [
                        "frontend.FollowedProduct",
                        "issue.Issue",
                        "prodmgmt.Application",
                        "prodmgmt.Product",
                        "release.DeploymentRequest",
                        "release.Release",
                        "release.ReleaseElement"
                    ],
                },
                {
                    "actions": ["change"],
                    "models": ["ci.BuildJob"],
                },
            ],
        },
        {
            "group": "Operations",
            "inherit_from": ["Users"],
            "grants": [
                {
                    "actions": ["add", "change", "delete"],
                    "models": [
                        "auth.Group",
                        "auth.User",
                        "ci.BuildServer",
                        "deployment.DeploymentPreference",
                        "deployment.DeploymentSystem",
                        "issue.IssueTracker",
                        "issue.IssueTrackerProject",
                        "package.PackageRepository",
                        "prodmgmt.Person",
                        "system.Environment",
                        "system.InternetAddress",
                        "system.Node",
                        "system.NodeAddress",
                        "system.Pool",
                        "system.PoolMembership",
                        "system.Role",
                        "system.RoleMembership"
                    ],
                },
            ],
        },
    ],
}

SERIALIZATION_MODULES = {
    "xml" : "hotjazz.xml_serializer",
    "json" : "hotjazz.json_serializer",
    "xml_no_db" : "hotjazz.xml_serializer_no_db",
    "json_ext" : "hotjazz.json_serializer_ext",
}

SSL_CERT_FILE = '/etc/pki/crichton.pem'
SSL_KEY_FILE = '/etc/pki/crichton.pem'
CA_CERT_FILE = '/etc/ca.pem'

# Override the standard DeploymentRequest admin
# Accepted values are currently 'jira' or None
DEPLOYMENTREQUEST_EXTENSION = 'jira'

USE_TEST_JIRA_PROJECT = True
USE_TEST_JIRA_HOST = True

from socket import gethostname
hostname=gethostname()
if hostname in ["scom001.back.live.cwwtf.local", "scom101.back.live.telhc.local"]:
    USE_TEST_JIRA_PROJECT = False
    USE_TEST_JIRA_HOST = False

if USE_TEST_JIRA_PROJECT:
    OPS_PROJECT_NAME = "OPSTEST"
else:
    OPS_PROJECT_NAME = "OPS"
if USE_TEST_JIRA_HOST:
    JIRA_NAME = "forge-jira-test"
    JIRA_BASE_URL = 'https://jira-test.dev.domain.com:443/'
else:
    JIRA_NAME = "forge-jira"
    JIRA_BASE_URL = 'https://jira.dev.domain.com:443/'

# Jira passwords are normally random 32 character strings. The password below only works
# on the jira-test instance. On production, this value will come from local_settings.py
# which is placed on the server by puppet.
JIRA_USER = 'crichton'
JIRA_PASS = 'AspidistraPie'

JIRA_SOAP_ROOT = JIRA_BASE_URL + 'rpc/soap/jirasoapservice-v2?wsdl'
JIRA_REST_ROOT = JIRA_BASE_URL + 'rest/api/2.0.alpha1/'

# HAYSTACK_SITECONF = 'frontend.search_sites'
# todo determine search engine HAYSTACK_SEARCH_ENGINE = 'whoosh'


# SOCOM-213: don't use hard-coded names for logging directories; breaks in hudson
from os import environ, path
from os.path import abspath, dirname
LOGDIR_ROOT = "/"
if "SERVER_CLASS" in environ.keys() and environ["SERVER_CLASS"] == "ci-db":
    LOGDIR_ROOT = abspath(path.join(dirname(abspath(__file__)), ".."))
LOGDIR = abspath(path.join(LOGDIR_ROOT, "data/app-logs/crichton"))

import sys
from crichtonweb.system import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)-7s %(filename)15s:%(lineno)-4d [%(process)d]  %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)-7s %(message)s'
        },
    },
    'filters': {
        # none yet
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout
        },
        'crichtondebug':{
            'level':'DEBUG',
            'class':'logging.handlers.SafeRotatingFileHandler',
            'formatter': 'verbose',
            'filename': abspath(path.join(LOGDIR, 'debug_log')),
            'maxBytes': 1024*1024*10,
            'backupCount': 10
        },
        'crichtonweb':{
            'level':'ERROR',
            'class':'logging.handlers.SafeRotatingFileHandler',
            'formatter': 'simple',
            'filename': abspath(path.join(LOGDIR, 'web_error_log')),
            'maxBytes': 1024*1024*10,
            'backupCount': 10
        },
        'crichtoncron':{
            'level':'ERROR',
            'class':'logging.handlers.SafeRotatingFileHandler',
            'formatter': 'simple',
            'filename': abspath(path.join(LOGDIR, 'cron_error_log')),
            'maxBytes': 1024*1024*10,
            'backupCount': 10
        },
        'crichtoncli': {
            'level':'ERROR',
            'class':'logging.handlers.SafeRotatingFileHandler',
            'formatter': 'simple',
            'filename': abspath(path.join(LOGDIR, 'cli_error_log')),
            'maxBytes': 1024*1024*10,
            'backupCount': 10
        },
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['crichtonweb', 'crichtondebug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'crichtonweb': {
            'handlers': ['crichtonweb', 'crichtondebug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'crichtoncron': {
            'handlers': ['crichtoncron', 'crichtondebug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'crichtoncli': {
            'handlers': ['crichtoncli', 'crichtondebug', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'suds': {
            'handlers':['null'],
            'propagate': True,
            'level':'ERROR',
        }
    }
}

# Can't see how to get at this standard Template Context Processors tuple
# because it's not set at the point.
# so it seems you need to list them all manually in order to be able to add the request one.
TEMPLATE_CONTEXT_PROCESSORS = (\
    # the standard ones
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    # the extra one
    'django.core.context_processors.request',
    )


AJAX_LOOKUP_CHANNELS = {
    'build_job': ('ci.lookups', 'BuildJobLookup'),
    'orphan_build_job': ('ci.lookups', 'OrphanBuildJobLookup'),
    'recipe': ('deployment.lookups', 'RecipeLookup'),
    'product_deployment': ('deployment.lookups', 'ProductDeploymentLookup'),
    'issue': ('issue.lookups', 'IssueLookup'),
    'ops_issue': ('issue.lookups', 'OpsIssueLookup'),
    'pipeline_issue': ('issue.lookups', 'PipelineIssueLookup'),
    'package': ('package.lookups', 'PackageLookup'),
    'package_name': ('package.lookups', 'PackageNameLookup'),
    'version': ('package.lookups', 'VersionLookup'),
    'application': ('prodmgmt.lookups', 'ApplicationLookup'),
    'person': ('prodmgmt.lookups', 'PersonLookup'),
    'product': ('prodmgmt.lookups', 'ProductLookup'),
    'release': ('release.lookups', 'ReleaseLookup'),
    'node': ('system.lookups', 'NodeLookup'),
    'internet_address': ('system.lookups', 'InternetAddressLookup'),
}
MAX_LOOKUP_RESULTS=20 # for now only used in package.lookups.PackageLookup. TODO: eval using everywhere

# the below snippet to override the above settings (shipped in the rpm)
# with any machine local settings, especially useful for things like
# DATABASES. See local_settings.py.dist for an example.
LOCAL_SETTINGS_SEARCH_PATHS = ['/etc/', '/etc/crichton', '/usr/local/etc', '/usr/local/etc/crichton']
import sys
for mypath in LOCAL_SETTINGS_SEARCH_PATHS:
    sys.path.insert(0, mypath)
try: 
    from local_settings import *
except ImportError:
    pass
for i in range(0,len(LOCAL_SETTINGS_SEARCH_PATHS)):
    del sys.path[0]

# eof
