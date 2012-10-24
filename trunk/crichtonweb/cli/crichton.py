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
import signal
from os import path
from os.path import dirname, abspath

thisdir = dirname(abspath(__file__))

crichtonwebdir = "/usr/local/crichtonweb"
if path.exists(crichtonwebdir):
    sys.path.insert(0, abspath(path.join(crichtonwebdir, "..")))
    sys.path.insert(0, crichtonwebdir)

crichtonwebdir = abspath(path.join(thisdir, '..', '..', 'crichtonweb'))
if path.exists(crichtonwebdir):
    sys.path.insert(0, abspath(path.join(crichtonwebdir, "..")))
    sys.path.insert(0, crichtonwebdir)

crichtonclidir = "/usr/local/crichtoncli"
if path.exists(crichtonclidir):
    sys.path.append(crichtonclidir)

sys.path.insert(0, thisdir)

# django initialization
#   http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/
from django.core.management import setup_environ
import settings
setup_environ(settings)

# die gracefully
def shutDown(sig, frame):
    #print 'In shutDown() -> shutting down signal:%s recived' % repr(sig)
    sys.exit(0)

# use a main() method in case we want to call this programmatically for testing.
def main(cmd):
    from crichtoncli import execute_from_command_line
    execute_from_command_line(cmd)
    
if __name__ == "__main__":

    # catch CTRL-C, could be done through "KeyboardInterrupt"
    signal.signal(signal.SIGINT, shutDown)

    main(sys.argv)
