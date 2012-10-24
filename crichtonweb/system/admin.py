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

from crichtonweb.admin import mysite
import crichtonweb.system.models as system
import crichtonweb.deployment.admin_inline as deployment_inline
from crichtonweb.core.register import register
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.admin.options import ModelAdmin
import crichtonweb.system.admin_inline as system_inline
import crichtonweb.package.admin_inline as package_inline
from crichtonweb.system.forms import NodeAddressForm, PoolMembershipForm, RoleMembershipForm, PackageInstallationForm

#
# Admins
#


class EnvironmentAdmin(AuditedAdmin):
    list_display = ('name', 'deployment_preference_list_urls', 'deleted')
    list_display_links = ('name',)
    list_filter = ('deleted',)
    fields = ('name', 'deleted')
    search_fields = ('name',)
    inlines = [deployment_inline.DeploymentPreferenceInline, system_inline.PoolInline,
               system_inline.PackageRepositoryEnvironmentInline]

class NodeAdmin(AuditedAdmin):
    list_display = ('name', 'environment_url', 'is_virtual', 'internet_address_list', 'pool_list_urls', 'deleted')
    list_display_links = ('name',)
    list_filter = ('environment', 'deleted', 'is_virtual')
    fields = ('name', 'environment', 'is_virtual', 'deleted')
    search_fields = ('name',)
    inlines = [system_inline.PoolMembershipInline, system_inline.NodeAddressInline]

class NodeAddressAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted',)
    fields = ('node', 'address', 'deleted')
    search_fields = ('node__name', 'address__address')
    form = NodeAddressForm

class PoolAdmin(AuditedAdmin):
    list_display = ('name', 'environment', 'deleted')
    list_display_links = ('name',)
    list_filter = ('environment', 'deleted')
    fields = ('name', 'environment', 'role', 'deleted')
    search_fields = ('name', 'environment', 'role__name')
    inlines = [system_inline.PoolMembershipInline]

class PoolMembershipAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted',)
    fields = ('node', 'pool', 'deleted')
    search_fields = ('node__name', 'pool__name')
    form = PoolMembershipForm

class RoleAdmin(AuditedAdmin):
    list_display = ('name', 'deleted')
    list_display_links = ('name',)
    list_filter = ('deleted',)
    fields = ('name', 'deleted')
    search_fields = ('name',)
    inlines = [system_inline.RoleMembershipInline]

class RoleMembershipAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted',)
    fields = ('role', 'application', 'deleted')
    search_fields = ('role__name', 'application__name')
    form = RoleMembershipForm

class PackageInstallationAdmin(ModelAdmin):
    list_display = ('package', 'node', 'first_seen', 'not_seen')
    list_display_links = ('package', 'node')
    fields = ('package', 'node', 'first_seen', 'not_seen')
    search_fields = ('package__name', 'package__version__name', 'node__name')
    ordering = ('package__name', 'node__name')
    date_hierarchy = 'first_seen'
    can_delete = False
    form = PackageInstallationForm


# register them all

for model in [system.InternetAddress, system.Environment,
              system.Node, system.NodeAddress, system.Pool, 
              system.PoolMembership, system.Role, system.RoleMembership,
              system.PackageInstallation]:
    register(model, locals())

# eof
