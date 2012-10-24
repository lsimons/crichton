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

from distutils.core import setup    
import os

_version = None
def get_version():
    global _version
    if _version:
        return _version
    cwd = os.path.dirname(os.path.abspath(__file__))
    vfile = os.path.join(cwd, "VERSION")
    _version = open(vfile, 'r').read().strip()
    
    # get variables out of hudson (if building from hudson)
    svn_revision = os.environ.get("SVN_REVISION", False)
    if svn_revision:
        # rpmbuild feels this should be _ not space
        _version += "_" + svn_revision
    build_number = os.environ.get("BUILD_NUMBER", False)
    if build_number:
        _version += "." + build_number
    
    return _version

setup(
    name = "crichtoncron",
    version = get_version(),
    url = 'https://confluence.dev.domain.com/display/socom/SoCoM',
	download_url = 'https://confluence.dev.domain.com/display/socom/SoCoM',
    license = 'Commercial',
    description = "crichton is a configuration management database.",
    # long_description is only here to keep rpm happy
    long_description = "crichton is a configuration management database.",
    author = 'Leo Simons',
    author_email = 'mail@leosimons.com',
    packages = [
        'crichtoncron',
        'crichtoncron.commands',
    ],
    data_files = [
        ('/etc/cron.d', [
            'crichton.cron',
        ]),
        ('/usr/local/crichtoncron', [
            'indexhudson.sh',
            'indexjira.sh',
            'indexrpm.sh',
            'indexyum.sh',
            'indexzenoss.sh',
            'crichtoncron.conf',
            'crichtoncron.py',
        ]),
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
    ]
)
