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
class sudoers {
    # https://repo.domain.comforge/infrastructure/production/puppet/
    #     modules/sudoers/manifests/init.pp

    if $server_env == 'sandbox' {    
        package { ["sudo"]:
            ensure => latest,
        }
        file { '/etc/sudoers':
            ensure => present,
            #content => template("sudoers/sudoers.erb"),
            source => 'puppet:///modules/sudoers/sudoers',
            owner => 'root',
            group => 'root',
            mode => 440,
        }
    }
    # we are not using devmanage user, so let's stop hacking
    # else {
        # On the platform, just add support for the devmanage user,
        # sudoers will vary server to server so can't overwrite the whole file.
        # In addition, there's a good change it'll be overwritten with the proper
        # puppet so for now this makes it fairly easy to put it back.
        # When we have dev environments sorted out properly this change should be 
        # requested from the livesite team so it becomes part of the main sudoers module.
    #    exec { "echo -e 'Defaults:devmanage !requiretty\ndevmanage ALL= NOPASSWD: /usr/sbin/puppetd *\ndevmanage ALL= NOPASSWD: /home/devmanage/bin/*\ndevmanage ALL= NOPASSWD: /sbin/service *\ndevmanage ALL= NOPASSWD: /bin/rpm *\ndevmanage ALL= NOPASSWD: /usr/bin/yum *\ndevmanage ALL= NOPASSWD: /usr/local/bin/enable_site *' >> /etc/sudoers":
    #        onlyif => 'test `grep -c devmanage /etc/sudoers` -eq 0',
    #    }
    #}
}
