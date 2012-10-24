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
class buildserver {
    # Repo tools:
    package { ['createrepo', 'repo-maintenance']:
        ensure => latest,
        require => Yumrepo["live"];
    }

    # Repo base dir & httpd conf
    file { "/data/yum.domain.local":
        ensure => directory,
        owner => root,
        group => root,
        mode => 755,
        require => File['/data'],
    }
    file { "/data/yum.domain.local/docroot":
        ensure => directory,
        owner => root,
        group => root,
        mode => 755,
        require => File['/data/yum.domain.local'],
    }
    file { '/etc/httpd/conf.d/yum.domain.local.conf':
        ensure => present,
        source => 'puppet:///modules/buildserver/httpd/yum.domain.local.conf',
        owner  => root,
        group  => root,
        mode   => 644,
        require => Package['httpd'],
        notify  => Service['httpd'],
    }

    include buildserver::stagerepo
    include buildserver::liverepo
}

define localyumrepo() {
    file { "/data/yum.domain.local/docroot/$name":
        ensure => directory,
        owner => root,
        group => root,
        mode => 755,
        require => File['/data/yum.domain.local/docroot'],
    }
    file { "/data/yum.domain.local/docroot/$name/repodata":
        ensure => directory,
        owner => root,
        group => root,
        mode => 755,
        require => File["/data/yum.domain.local/docroot/$name"],
    }
    file { "/data/yum.domain.local/docroot/$name/noarch":
        ensure => directory,
        owner => root,
        group => root,
        mode => 755,
        require => File["/data/yum.domain.local/docroot/$name"],
    }
    file { "/data/yum.domain.local/docroot/$name/x86_64":
        ensure => directory,
        owner => root,
        group => root,
        mode => 755,
        require => File["/data/yum.domain.local/docroot/$name"],
    }
    file { "/data/yum.domain.local/docroot/$name/reindex.sh":
        source => "puppet:///modules/buildserver/$name/reindex.sh",
        owner => root,
        group => root,
        mode => 755,
        require => File["/data/yum.domain.local/docroot/$name"],
    }
    exec { "/data/yum.domain.local/docroot/$name/reindex.sh":
        creates => "/data/yum.domain.local/docroot/$name/repodata/primary.xml.gz",
        require => [ File["/data/yum.domain.local/docroot/$name/reindex.sh"], Package['createrepo'] ]
    }
}

class buildserver::stagerepo {
    localyumrepo { "stage": }
    # Helper script to promote rpms to stage repo
    file { "/usr/local/bin/promote-to-stage":
        source => "puppet:///modules/buildserver/stage/promote-to-stage",
        owner => root,
        group => root,
        mode => 755,
        require => Package['repo-maintenance'],
    }
}

class buildserver::liverepo {
    localyumrepo { "live": }
    # Helper script to promote rpms to live repo
    file { "/usr/local/bin/promote-to-live":
        source => "puppet:///modules/buildserver/live/promote-to-live",
        owner => root,
        group => root,
        mode => 755,
        require => Package['repo-maintenance'],
    }
}
