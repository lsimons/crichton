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
class mysqlserver {

        include mysqlserver::config
        $replication             = $mysqlserver::config::replication
        $server_id               = $mysqlserver::config::server_id
        $interface               = $mysqlserver::config::interface
        $innodb_buffer_pool_size = $mysqlserver::config::innodb_buffer_pool_size
        $query_cache_size        = $mysqlserver::config::query_cache_size
        $replication_acl_mask    = $mysqlserver::config::replication_acl_mask
        $replication_password    = $mysqlserver::config::replication_password

        # 20110228 - DMI uses SSL with client certs for MySQL, disable
        # pki::servercert { "local": owner => "mysql" } # XXX dep fail with mysql user

        package { "mysql":        ensure => latest }
        package { "mysql-server": ensure => latest }

        service { "mysqld":
                ensure     => running,
                enable     => true,
                hasrestart => true,
                hasstatus  => true,
                require    => [ Package["mysql-server"], Exec["Setup MySQL data directory"] ]
        }

        file { "my.cnf":
                name    => "/etc/my.cnf",
                content => template("mysqlserver/my.cnf.erb"),
                owner   => "root",
                group   => "root",
                mode    => 644,
                notify  => Service[mysqld],
                require => Package["mysql-server"]
        }

        file { 
                "/data/mysql":
                        ensure => directory;
                "/data/mysql/db":
                        ensure  => directory,
                        owner   => "mysql",
                        group   => "mysql",
                        require => Package["mysql-server"],
                        mode    => 750;
                "/data/mysql/log":
                        ensure  => directory,
                        owner   => "mysql",
                        group   => "mysql",
                        require => Package["mysql-server"],
                        mode    => 750;
                "/data/mysql/log/bin":
                        ensure  => directory,
                        owner   => "mysql",
                        group   => "mysql",
                        require => Package["mysql-server"],
                        mode    => 750;
                "/data/mysql/log/relay":
                        ensure  => directory,
                        owner   => "mysql",
                        group   => "mysql",
                        require => Package["mysql-server"],
                        mode    => 750;
                "/data/mysql/backup":
                        ensure  => directory,
                        owner   => "mysql",
                        group   => "admins",
                        require => [ Package["mysql-server"], Group["admins"] ],
                        mode    => 750;
                "/data/mysql/tmp":
                        ensure  => directory,
                        owner   => "mysql",
                        group   => "mysql",
                        require => Package["mysql-server"],
                        mode    => 750;
        }

        file { "set-mysql-root-password":
                name   => "/usr/local/bin/set-mysql-root-password",
                ensure => present,
                source => "puppet:///modules/mysqlserver/set-mysql-root-password",
                owner  => "root",
                group  => "root",
                mode   => 555,
        }

        file { "slavectl":
                name    => "/usr/local/bin/slavectl",
                ensure  => present,
                content => template("mysqlserver/slavectl.erb"),
                owner   => "root",
                group   => "root",
                mode    => 550, # deliberately not o+r
        }

        file { "masterctl":
                name    => "/usr/local/bin/masterctl",
                ensure  => present,
                content => template("mysqlserver/masterctl.erb"),
                owner   => "root",
                group   => "root",
                mode    => 555,
        }

        file { "/usr/local/bin/mysql-dump":
                ensure  => present,
                content => template("mysqlserver/mysql-dump.erb"),
                owner   => "root",
                group   => "root",
                mode    => 555,
        }

        file { "/usr/local/bin/mysql-restore":
                ensure  => present,
                content => template("mysqlserver/mysql-restore.erb"),
                owner   => "root",
                group   => "root",
                mode    => 555,
        }

        file { "default-grants.sql":
                name    => "/usr/local/etc/default-grants.sql",
                ensure  => present,
                content => template("mysqlserver/default-grants.sql.erb"),
                owner   => "root",
                group   => "root",
                mode    => 440,
        }

        exec { "Setup MySQL data directory":
                subscribe   => Package["mysql-server"],
                refreshonly => true,
                unless      => "[ -d /data/mysql/db/mysql ]",
                require     => [ File["my.cnf"], File["/data/mysql/log/bin"] ],
                command     => "mysql_install_db > /var/tmp/mysql_install_db.log 2>&1 && chown -R mysql:mysql /data/mysql/db",
        }

        exec { "Set random MySQL root password":
                subscribe   => Package["mysql-server"],
                refreshonly => true,
                path        => "/bin:/usr/bin:/usr/local/bin",
                require     => [ Service["mysqld"], File["set-mysql-root-password"] ],
                command     => "set-mysql-root-password",
        }

        exec { "Issue replication and housekeeping GRANTs":
                subscribe   => File["default-grants.sql"],
                refreshonly => true,
                require     => Service["mysqld"],
                command     => "mysql < /usr/local/etc/default-grants.sql",
                environment => [ "HOME=/root" ],
        }

        cron { "mysql-backup":
                command => "/usr/local/bin/mysql-dump", # XXX lockrun this
                ensure  => present,
                user    => root,
                hour    => 02,
                minute  => 00,
        }
}

# vim: set sw=8 ts=8:
