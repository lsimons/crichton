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

# this is needed because otherwise you can get this error:
#   Parameter unless failed: '[ -d /data/mysql/db/mysql ]'
#   is both unqualifed and specified no search path at
#   /etc/puppet/development/modules/mysqlserver/manifests/init.pp:136
Exec {
  path => ['/usr/local/sbin',
    '/usr/local/bin',
    '/sbin',
    '/bin',
    '/usr/sbin',
    '/usr/bin']
}

# this directory is needed to run puppet on local manifests...
file { '/var/lib/puppet/reports':
  ensure => directory,
  owner => "puppet",
  group => "puppet",
  mode => 755
}

# from https://repo.domain.comforge/infrastructure
#      /production/puppet/modules/users/manifests/admins.pp
group { 'admins':
  gid => 1500,
}

# from https://repo.domain.comforge/infrastructure
#      /production/puppet/modules/platform-base/manifests/init.pp
file { "/data":
    ensure => directory,
    owner => root,
    group => root,
    mode => 755
}

class fabric-runner {
    include sudoers
    include fabbed
    include buildserver
    yumrepo { "fabric-stage":
        descr => 'Local Stage Repo',
        baseurl => "http://localhost:8800/stage/",
        enabled => 1,
        gpgcheck => 0,
        metadata_expire => 1,
        require => Exec["/data/yum.forge.local/docroot/stage/reindex.sh"]
    }
    yumrepo { "fabric-live":
        descr => 'Local Live Repo',
        baseurl => "http://localhost:8800/live/",
        enabled => 1,
        gpgcheck => 0,
        metadata_expire => 1,
        require => Exec["/data/yum.forge.local/docroot/live/reindex.sh"]
    }
}

class crichtonserver-profile {
  include users::crichton
  include system
  include crichtonserver::httpd
  include crichtonserver::repos
  include mysqlserver
  include crichtonserver::crichtonweb
}

# 'forge' is the hostname for leo's sandbox
node forge {
  include sudoers
  include fabbed
}

node crichton {
  include crichtonserver-profile
  # removed due to it breaking Reith sandboxes SOCOM-346
  #include fabric-runner
}

# our dev server
node build005 {
  # hmm, seems weird that rsync is not installed by default...
  # ...this is needed to run update-build005.sh
  package { "rsync": ensure => present }

  include crichtonserver-profile
  include fabric-runner
}
