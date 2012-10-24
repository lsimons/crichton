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
# todo remove, this duplicates production/puppet/repos/manifests/init.pp::repos
class crichtonserver::repos {
    if $server_env == "sandbox" {
        yumrepo { "live":
            descr => 'Live Repo',
            baseurl => 'https://yum.domain.mine/live/',
            enabled => 1,
            gpgcheck => 0,
            metadata_expire => 1,
        }
        yumrepo { "int":
            descr => 'Int Repo',
            baseurl => 'https://yum.domain.mine/int/',
            enabled => 1,
            gpgcheck => 0,
            metadata_expire => 1,
        }
    } else {
        yumrepo { "live":
            descr => 'Live Repo',
            baseurl => 'http://yum.domain.local/live/',
            enabled => 1,
            gpgcheck => 0,
            metadata_expire => 1,
        }
        yumrepo { "int":
            descr => 'Int Repo',
            baseurl => 'http://yum.domain.local/int/',
            enabled => 1,
            gpgcheck => 0,
            metadata_expire => 1,
        }
    }
}

# todo remove, this duplicates production/puppet/httpd/manifests/init.pp::httpd
class crichtonserver::httpd {
    package { "httpd":
        ensure=> latest,
        require => Yumrepo["live"],
        notify => Service[httpd],
    }
    file { "/var/log/httpd":
        require => Package["httpd"],
        ensure => directory,
        owner => root,
        group => root,
        mode  => 755
    }
    package { "libselinux":
        ensure=> latest,
        require => Yumrepo["live"],
        before => Service[httpd],
    }
    service { "httpd":
        enable => true,
        require => Package[httpd],
        ensure => running,
        hasstatus => true,
    }
}

class crichtonserver::crichtonweb inherits crichtonserver::httpd {
    package { [ "python", "python-suds" ]:
        ensure => latest,
        require => [Yumrepo["live"]]
    }
    
    package { [ "mod_ssl", "catools", "httpd-ssl-certcheck" ]:
        ensure => latest,
        require => [Package[httpd],Yumrepo["live"]]
    }
    
    package { "mod_wsgi":
        ensure => latest,
        require => [Package[httpd]]
    }
    
    package { "teleportd":
        ensure => latest
    }
    
    package { [ "cronwrap", "multiprocessing" ]:
        ensure => latest,
        require => [Yumrepo["live"]]
    }

    # todo I think this may belong in the httpd class
    file { "/etc/httpd/conf.d":
        ensure => directory,
        owner => root,
        group => root,
        mode => 750,
        require => Package['httpd']
    }

    file { "/data/crichton":
        ensure => directory,
        owner => crichton,
        group => crichton,
        mode => 755,
        require => User['crichton']
    } 

    file { "/data/crichton/html":
        ensure => directory,
        owner => crichton,
        group => crichton,
        mode => 755,
        require => File['/data/crichton']
    }

    file { "/data/crichton/yum":
        ensure => directory,
        owner => crichton,
        group => crichton,
        mode => 755,
        require => File['/data/crichton']
    }

    file { "/etc/pki/crichton.key":
        #ensure  => present,
        #source  => "puppet:///modules/secure/socom/crichton.key",
        owner   => "apache",
        group   => "crichton",
        mode    => 440,
        require => User['crichton']
    }

    file { "/etc/pki/crichton.pem":
        #ensure  => present,
        #source  => "puppet:///modules/secure/socom/crichton.pem",
        owner   => "apache",
        group   => "crichton",
        mode    => 440,
        require => User['crichton']
    }

    package { [
          "Django",
          "django-audit-log",
          "django-haystack",
          "South",
          "httplib2",
          "MySQL-python",
          ]:
        ensure => latest,
        require => [Yumrepo["int"]]
    }
    
    # TODO ssl certs for crichton
    # if $server_env != "sandbox" {
    #     file { "/etc/crichton-test.domain.mine.pem":
    #         source => "puppet:///modules/secure/crichtonserver/crichton-test.domain.mine.pem",
    #         owner => root,
    #         group => root,
    #         mode => 400,
    #         notify => Service['httpd'],
    #         before => Service['httpd'],
    #     }
    #     file { "/etc/crichton-test.domain.mine.key":
    #         source => "puppet:///modules/secure/crichtonserver/crichton-test.domain.mine.key",
    #         owner => root,
    #         group => root,
    #         mode => 400,
    #         notify => Service['httpd'],
    #         before => Service['httpd'],
    #     }
    # }
    
    file { "/etc/httpd/conf.d/crichton.httpd.conf":
        content => template('crichtonserver/crichton.httpd.conf.erb'),
        owner => root,
        group => root,
        mode => 644,
        require => [
          Package['httpd'],
          Package['mod_ssl'],
          Package['catools'],
          Package['httpd-ssl-certcheck'],
          Package['mod_wsgi'],
          File['/etc/httpd/conf.d'],
          File['/data/crichton/html'] ],
        notify => Service['httpd'],
    }
    
    # TODO ideally forge had an extensive custom mysql module, like
    #    https://github.com/camptocamp/puppet-mysql or
    #    https://github.com/timstoop/puppet-mysql/commits/development/
    # but we'll do just what we really need here, for now
    exec { "create-crichton-db":
        unless => "/usr/bin/mysql \
            --defaults-extra-file=/root/.my.cnf \
            -uroot \
            -e 'SELECT TRUE;' crichton",
        command => "/usr/bin/mysql \
            --defaults-extra-file=/root/.my.cnf \
            -uroot \
            -e 'CREATE DATABASE crichton;'",
        require => Service["mysqld"],
    }

    exec { "grant-crichton-db":
        unless => "/usr/bin/mysql \
            --defaults-extra-file=/root/.my.cnf \
            -ucrichton \
            -pronnocnhoj \
            -e 'SELECT TRUE;' \
            crichton",
        command => "/usr/bin/mysql \
            --defaults-extra-file=/root/.my.cnf \
            -uroot \
            -e \"GRANT ALL ON crichton.* TO crichton@localhost
                         IDENTIFIED BY 'ronnocnhoj';
                 FLUSH PRIVILEGES;\"",
        require => [Service["mysqld"], Exec["create-crichton-db"]]
    }

    # TODO this probably needs to go into the rpm for crichtonweb
    # but putting it here now until I figure out how to do that in distutils
    file { '/data/app-logs':
        ensure => directory,
        require => File['/data'],
        owner => root,
        group => root,
        mode => 755
    }
    file { '/data/app-logs/crichton/':
        ensure => directory,
        require => File['/data/app-logs'],
        owner => apache,
        group => apache,
        mode => 777
    }

    file { '/etc/crichton':
        ensure => directory,
        owner => root,
        group => root,
        mode => 755
    }
    file { '/etc/crichton/crichtoncron.conf':
        ensure => present,
        source => "puppet:///modules/crichtonserver/crichtoncron.conf",
        require => File['/etc/crichton'],
        owner => root,
        group => root,
        mode => 644
    }

    if $server_env != "sandbox" {
        package { "crichtonweb":
            ensure => latest,
            require => [
                Yumrepo["int"],
                Package["Django"],
                Package["django-audit-log"],
                Package["django-haystack"],
                Package["South"],
                Package["MySQL-python"],
            ],
        }
        
        package { "crichton-cli":
            ensure => absent,
        }
        package { "crichtoncli":
            ensure => latest,
            require => [
                Package["crichton-cli"],
                Package["crichtonweb"],
                Package["httplib2"],
            ],
        }
        
        package { "crichtoncron":
            ensure => latest,
            require => [
                Package["MySQL-python"],
                Package["cronwrap"],
                Package["crichtoncli"],
                Package["crichtonweb"],
            ],
        }

        # TODO - add this to crichtonweb rpm?        
        file { "/etc/logrotate.d/crichton":
                ensure => present,
                source => "puppet:///modules/crichtonserver/logrotate",
                owner  => "root",
                group  => "root",
                mode   => 644,
        }
        
        file { "crichton-migration-check":
                name   => "/usr/local/crichtonweb/crichton-migration-check",
                ensure => present,
                source => "puppet:///modules/crichtonserver/crichton-migration-check",
                owner  => "root",
                group  => "root",
                mode   => 550,
        }
        
        file { "ensure-django-admin-user":
                name   => "/usr/local/crichtonweb/ensure-django-admin-user",
                ensure => present,
                source => "puppet:///modules/crichtonserver/ensure-django-admin-user",
                owner  => "root",
                group  => "root",
                mode   => 550
        }
        
        exec { "crichtonweb-db-migrate":
            unless => "/usr/local/crichtonweb/crichton-migration-check",
            command => "/usr/local/crichtonweb/manage.py syncdb --noinput --migrate",
            require => [
                Service["mysqld"],
                Exec["create-crichton-db"],
                Exec["grant-crichton-db"],
                Package["crichtonweb"],
                File["crichton-migration-check"],
            ]
        }
        
        exec { "django-admin-user":
            refreshonly => true,
            command => "/usr/local/crichtonweb/ensure-django-admin-user \
                admin ronnocnhoj forge-eng@lists.forge.domain.local",
            require => [
                Service["mysqld"],
                Package["crichtonweb"],
                File["ensure-django-admin-user"]
            ],
            subscribe => Package["crichtonweb"],
        }

        exec { "applyauthconfig":
            refreshonly => true,
            command => "/usr/local/crichtonweb/applyauthconfig.py",
            require => [
                Service["mysqld"],
                Package["crichtonweb"],
            ],
            subscribe => Exec["crichtonweb-db-migrate"]
        }
        
        exec { "db-init.sh":
            refreshonly => true,
            command => "/usr/local/crichtoncli/db-init.sh",
            require => [
                Service["mysqld"],
                Package["crichtonweb"],
                Package["crichtoncli"],
            ],
            subscribe => Package["crichtonweb"],
        }
    }
}
