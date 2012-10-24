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
import crichtonweb.package.models as package
from crichtonweb.core.register import register
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.admin.options import ModelAdmin
from crichtonweb.package.forms import PackageForm, PackageLocationForm

class PackageAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted',)
    fields = ('name', 'version', 'deleted')
    search_fields = ('name', 'version__name')
    form = PackageForm

class PackageNameAdmin(AuditedAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    fields = ('name',)
    search_fields = ('name',)

class PackageLocationAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted', 'repository')
    fields = ('package', 'repository', 'deleted')
    search_fields = ('package__name',)
    form = PackageLocationForm

class VersionAdmin(ModelAdmin):
    list_display = ('name', 'major', 'minor', 'micro', 'build', 'revision', 'status')
    list_display_links = ('name',)
    list_filter = ('major', 'status')
    fields = ('name', 'major', 'minor', 'micro', 'build', 'revision', 'status', 'rpm_version', 'rpm_release')
    search_fields = ('name',)
    ordering = ('name',)
    can_delete = False

# register them all

for model in [package.Package, package.PackageName, package.Version,
        package.PackageRepository, package.PackageLocation]:
    register(model, locals())

# eof
