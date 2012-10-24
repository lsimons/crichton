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
import os
import sys
from os import path
from os.path import dirname, abspath

# needed when we explicitly specify DJANGO_SETTINGS_MODULE
DSM="DJANGO_SETTINGS_MODULE"
if DSM in os.environ and os.environ[DSM].endswith("test_settings"):
    from settings import *

thisdir = dirname(abspath(__file__))
sys.path.append(thisdir)
crichtoncli_dir = abspath(path.join(thisdir, 'cli'))
sys.path.append(crichtoncli_dir)

# Leo reverted the test database back to mysql with the following comment
    # see the svn commit log for SOCOM-121 as well as builds #235 through #249
    # for why we are now using the mysql backend when testing: there seems to be
    # a bug in south/django its use of sqlite3, or a bug in the python library
    # for sqlite3, or a bug in sqlite, that causes the line
    #   db.delete_column('release_releaseelement', 'package_obj_id')
    # in
    #   release/migrations/0006_SOCOM_11_release_element_package_rename_2.py
    # to fail with
    #       File "/usr/lib/python2.4/site-packages/django/db/backends/__init__.py", line 46, in _commit
    #         return self.connection.commit()
    #     OperationalError: SQL logic error or missing database
    #
#
# I (Rachel) cannot reproduce that mysql problem, so I am reverting it back to sqlite3 for speed.
#
DATABASES = {
    # use sqlite test database for speed
    
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdb',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'TEST_NAME': 'testdb.db',
    }
    ## 'default': {
    ##     'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    ##     'NAME': 'crichton',                      # Or path to database file if using sqlite3.
    ##     'USER': 'root',                      # Not used with sqlite3.
    ##     'PASSWORD': '',                  # Not used with sqlite3.
    ##     'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
    ##     'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    ## }
}

CACHE_BACKEND = 'locmem://'

# Uncomment following line to use lettuce for testing
#INSTALLED_APPS = INSTALLED_APPS + ('lettuce.django',)

INSTALLED_TEST_APPS = (
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ["--with-doctest", "--verbosity=2"]

# To run extra test from command line:
# PYTHONPATH=. DJANGO_SETTINGS_MODULE=settings nosetests --with-doctest core/models/

# some of the django.contrib unit tests make too many assumptions about
# the set up of the application to be of use. We always explicitly disable
# those tests here, so that "./manage.py test" (which tests _all_ our
# apps) works properly.
import types
import unittest
class DummyTest(unittest.TestCase):
    pass

_seen = []
def disable_nose_for(module, basename=None):
    if module in _seen:
        return
    _seen.append(module)
    if type(module) == types.StringType:
        __import__(module)
        module = sys.modules[module]
    if not basename:
        basename = module.__name__
    for k, v in module.__dict__.iteritems():
        t = type(v)
        if t == types.ModuleType:
            if v.__name__.startswith(basename):
                disable_nose_for(v.__name__, basename)
        elif t == types.ClassType or t == types.TypeType:
            if issubclass(v, unittest.TestCase):
                module.__dict__[k] = DummyTest
disable_nose_for('django.contrib.auth.tests')
disable_nose_for('django.contrib.messages.tests')

