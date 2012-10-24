#!/usr/bin/env bash
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

# this is a simple script that pushes ./development to
# puppet:/usr/puppet/development and then runs puppet on
# build005.

set -e

echo "Pushing latest puppet config"
rsync -e "ssh -o ClearAllForwardings=yes" \
    -a --delete \
    "./development/" \
    "access.forge.domain.local:~/development/"
ssh -o ClearAllForwardings=yes \
    access.forge.domain.local \
    "/usr/bin/rsync -e 'ssh -o ClearAllForwardings=yes' -a --delete ~/development/ build005:~/development/"

echo "Applying puppet config"
ssh -o ClearAllForwardings=yes \
    -t access.forge.domain.local \
    'ssh -o ClearAllForwardings=yes -t build005 "sudo /usr/bin/rsync -a --delete ~/development/ /etc/puppet/development/ && cd /etc/puppet/development && sudo /usr/bin/puppet --modulepath=/etc/puppet/development/modules --verbose site.pp"'
