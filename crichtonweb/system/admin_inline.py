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
from django.contrib import admin as origadmin
import crichtonweb.system.models as system
from crichtonweb.system.forms import PoolMembershipForm, NodeAddressForm, RoleMembershipForm

class PackageRepositoryEnvironmentInline(origadmin.TabularInline):
    model = system.Environment.repositories.through
    extra = 0
    
class PoolInline(origadmin.TabularInline):
    model = system.Pool
    extra = 0
    fields = ('name', 'environment', 'deleted')

class PoolMembershipInline(origadmin.TabularInline):
    model = system.PoolMembership
    extra = 0
    fields = ('pool', 'node', 'deleted')
    form = PoolMembershipForm

class NodeAddressInline(origadmin.TabularInline):
    model = system.NodeAddress
    extra = 0
    fields = ('node', 'address', 'deleted')
    form = NodeAddressForm

class RoleMembershipInline(origadmin.TabularInline):
    model = system.RoleMembership
    extra = 0
    fields = ('role', 'application', 'deleted')
    form = RoleMembershipForm
