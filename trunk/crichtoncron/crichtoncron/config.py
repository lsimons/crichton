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
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser # python3, we can be optimistic can't we?

config_locations=['%s/crichtoncron.conf' % x for x in ['/usr/local/crichtoncron','.','/etc','/etc/crichton','/usr/local/etc','/usr/local/etc/crichton']]
config_locations.append(os.path.expanduser('~/.crichtoncron.conf'))
config_locations.reverse()

conf = ConfigParser.ConfigParser(os.environ)

_read_config = False
for config_location in config_locations:
    if os.path.exists(config_location):
        _read_configs = conf.read(config_location)
        if len(_read_configs) == 0:
            raise Exception("Cannot read config " + config_location)
        _read_config = True
        break
        
if not _read_config:
    raise Exception("Cannot find config " + " nor ".join(config_locations))

_crichtonwebconf = conf.get("crichtoncron", "crichtonwebconf")
_crichtonwebconfdir = os.path.dirname(_crichtonwebconf)
_crichtonwebconfname = os.path.basename(_crichtonwebconf)[:-3]

sys.path.insert(0,_crichtonwebconfdir)
__import__(_crichtonwebconfname)
crichtonweb_settings = sys.modules[_crichtonwebconfname]
del sys.path[0]
