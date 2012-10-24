#!/usr/bin/env python
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

import sys
from os import path
from os.path import dirname, abspath
import django.conf

thisdir = dirname(abspath(__file__))

crichtonwebdir = "/usr/local/crichtonweb"
if path.exists(crichtonwebdir):
    sys.path.insert(0, abspath(path.join(crichtonwebdir, "..")))
    sys.path.insert(0, crichtonwebdir)

crichtonwebdir = abspath(path.join(thisdir, '..', 'crichtonweb'))
if path.exists(crichtonwebdir):
    sys.path.insert(0, abspath(path.join(crichtonwebdir, "..")))
    sys.path.insert(0, crichtonwebdir)

crichtoncrondir = "/usr/local/crichtoncron"
if path.exists(crichtoncrondir):
    sys.path.append(crichtoncrondir)

sys.path.insert(0, thisdir)

# django initialization
#   http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/
from django.core.management import setup_environ
import settings
setup_environ(settings)
# Settings are imported lazily, so this is a bit of a hack to force the 
# conf module to load them now, otherwise things like logging don't work
# properly (this would normally be called somewhere in Django's internals)
django.conf.settings._setup()
from crichtonweb.system.logging import cron_log as logger

from crichtoncron import dblock
from crichtoncron.commands import get_commands

_commands = get_commands()

_command = sys.argv[1]
if not _command in _commands:
    raise Exception("Don't know command %s" % (_command,))

dblock.initdb()
dblock.lock(_command)
try:
    try:
        # it's almost perl, does that make it bad?
        _commands[_command]()
    except Exception, e:
        logger.exception(e)
        raise
finally:
    dblock.unlock(_command)
