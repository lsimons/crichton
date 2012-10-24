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
# fabric app_deploy wants a 'devmanage' user on target machines.
# These devmanage users then get an rbash which allows running
# just a few specific commands with NOPASSWD sudo applied to
# them. So the sudoers module is also needed.

class fabbed {
    ### users::devmanage
    group { 'manage':
        gid => 1623,
    }

    user { 'devmanage':
        ensure     => present,
        uid        => 9025,
        gid        => 1623,
        comment    => 'Platform Management User',
        home       => '/home/devmanage',
        shell      => '/bin/rbash',
        managehome => true,
        require    => [ File['/bin/rbash'], Group['manage'] ],
    }
    
    ### set your own ssh key here
    file { '/home/devmanage/.ssh/authorized_keys':
        ensure  => present,
        owner   => 'root',
        group   => 'manage',
        mode    => 750,
        source  => 'puppet:///modules/fabbed/authorized_keys',
        require => [ User['devmanage'], File['/home/devmanage/.ssh'] ],
    }
    
    # devmanage user doesn't have write permission on its home or SSH files
    file { '/home/devmanage':
        ensure => directory,
        owner  => 'root',
        group  => 'manage',
        mode   => 750,
        require => [ User['devmanage'], Group['manage'] ],
    }
    file { '/home/devmanage/.ssh':
        ensure  => directory,
        owner   => 'root',
        group   => 'manage',
        mode    => 750,
        require => File['/home/devmanage'],
    }
    
    # local bin directory
    file { '/home/devmanage/bin':
        ensure => directory,
        owner  => 'root',
        group  => 'manage',
        mode   => 750,
        require => File['/home/devmanage'],
    }
    
    # populate ~devmanage/bin with sudo and some utilities
    file { '/home/devmanage/bin/sudo':
        ensure => '/usr/bin/sudo'
    }
    
    file { '/home/devmanage/bin/puppetd':
        ensure => present,
        source => 'puppet:///modules/fabbed/puppetd',
        owner  => 'root',
        group  => 'root',
        mode   => 555,
        require => File['/home/devmanage/bin'],
    }
    file { '/home/devmanage/bin/facter':
        ensure => present,
        source => 'puppet:///modules/fabbed/facter',
        owner  => 'root',
        group  => 'root',
        mode   => 555,
        require => File['/home/devmanage/bin'],
    }
    
    # profile sets PATH to just ~devmanage/bin
    file { '/home/devmanage/.profile':
        ensure => present,
        source => 'puppet:///modules/fabbed/profile',
        owner  => 'root',
        group  => 'root',
        mode   => 444,
        require => File['/home/devmanage'],
    }
    file { '/home/devmanage/.bashrc':
        ensure => present,
        source => 'puppet:///modules/fabbed/profile',
        owner  => 'root',
        group  => 'root',
        mode   => 444,
        require => File['/home/devmanage'],
    }
    file { '/home/devmanage/.bash_profile':
        ensure => absent,
    }
    
    # rbash is a symlink to bash
    file { '/bin/rbash':
        ensure => '/bin/bash',
    }
    
    ### users::devmanage::remotedeploy
    file { '/home/devmanage/bin/install-rpms.py':
        ensure => present,
        source => 'puppet:///modules/fabbed/install-rpms.py',
        owner  => 'root',
        group  => 'root',
        mode   => 555,
    }
    # looks in /etc/httpd
    file { '/home/devmanage/bin/is-site-enabled':
        ensure => present,
        source => 'puppet:///modules/fabbed/is-site-enabled',
        owner  => 'root',
        group  => 'root',
        mode   => 555,
    }
    file { '/home/devmanage/bin/service':
        ensure => present,
        source => 'puppet:///modules/fabbed/service',
        owner  => 'root',
        group  => 'root',
        mode   => 555,
    }
}
