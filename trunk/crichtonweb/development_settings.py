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
from os.path import dirname, abspath

# I don't get why it is ever bad to just load evertyhing here. Loading
# everything gets rid of a test error I get sometimes:
# ======================================================================
# ERROR: Failure: NameError (name 'MIDDLEWARE_CLASSES' is not defined)
# ----------------------------------------------------------------------
# Traceback (most recent call last):
#   File "/Library/Python/2.6/site-packages/nose/loader.py", line 390, in loadTestsFromName
#     addr.filename, addr.module)
#   File "/Library/Python/2.6/site-packages/nose/importer.py", line 39, in importFromPath
#     return self.importFromDir(dir_path, fqname)
#   File "/Library/Python/2.6/site-packages/nose/importer.py", line 86, in importFromDir
#     mod = load_module(part_fqname, fh, filename, desc)
#   File "/Users/lsimons/bbc/svn/tools/crichton/trunk/crichtonweb/development_settings.py", line 16, in <module>
#     for mw in MIDDLEWARE_CLASSES:
# NameError: name 'MIDDLEWARE_CLASSES' is not defined
# # needed when we explicitly specify DJANGO_SETTINGS_MODULE
# DSM="DJANGO_SETTINGS_MODULE"
# if DSM in os.environ and os.environ[DSM] == "development_settings":
#     from settings import *
from settings import *

thisdir = dirname(abspath(__file__))
sys.path.append(thisdir)
crichtoncli_dir = abspath(os.path.join(thisdir, 'cli'))
sys.path.append(crichtoncli_dir)

new_mw = []
for mw in MIDDLEWARE_CLASSES:
    if mw.endswith('BBCRemoteUserMiddleware'):
        continue
    new_mw.extend(mw)
MIDLEWARE_CLASSES=tuple(new_mw)

try:
    del AUTHENTICATION_BACKENDS
except NameError:
    pass

