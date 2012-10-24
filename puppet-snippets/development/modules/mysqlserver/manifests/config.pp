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
class mysqlserver::config {
  case $hostname {
    # forge: {
    #   $replication = false
    #   $server_id   = 2001
    # }
    # build005: {
    #   $replication = false
    #   $server_id   = 2002
    # }
    default: {
      $replication = false
      $server_id   = 2002
    }
  }

  case $server_env {
    sandbox: {
      $innodb_buffer_pool_size = 128
      $query_cache_size        = 8
      $replication_acl_mask    = '172.16.64.%'
      $replication_password    = 'basebuild'
      $interface               = 'eth0'
    }
    green: {
      $innodb_buffer_pool_size = 4096
      $query_cache_size        = 256
      $replication_acl_mask    = '172.23.40.%'
      $replication_password    = 'p@ssw0rd'
      $interface               = 'eth0'
    }
    default: {
      $innodb_buffer_pool_size = 1024
      $query_cache_size        = 128
      $replication_acl_mask    = '172.23.40.%'
      $replication_password    = 'p@ssw0rd'
      $interface               = 'eth0'
    }
  }
}
