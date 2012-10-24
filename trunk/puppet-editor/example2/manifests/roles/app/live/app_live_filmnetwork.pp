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
class app::live::filmnetwork inherits app::live {
    package { "apache-tomcat-filmnetwork": ensure => "6.1.27-265113.10" }
    package { "bbc-war-filmnetwork": ensure => "0.1.0-308034.142" }
    appserver::tomcat-app { 'filmnetwork' }
}
