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
import crichtonweb.requirement.models as requirement
from crichtonweb.core.register import register
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.admin.admin_audit import ModelAdmin
import crichtonweb.requirement.admin_inline as requirement_inline
from crichtonweb.requirement.forms import PackageSpecificationForm, RequirementForm, VersionRangeForm

class EnvironmentRequirementAdmin(ModelAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    fields = ('requirement', 'specification', 'environment', 'deleted')
    raw_id_fields = ('requirement', 'specification')
    list_filter = ('deleted',)
    search_fields = ('requirement__application__name', 'environment__name',
            'specification__package__name')

class PackageSpecificationAdmin(ModelAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    fields = ('package', 'version_specification', 'deleted')
    raw_id_fields = ('version_specification',)
    list_filter = ('deleted',)
    search_fields = ('package__name', 'version_specification__version__name',
            'version_specification__version_range__name')
    form = PackageSpecificationForm

class RequirementAdmin(ModelAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    fields = ('application', 'default_specification', 'deleted')
    raw_id_fields = ('default_specification',)
    list_filter = ('deleted',)
    search_fields = ('application__name',)
    inlines = [requirement_inline.EnvironmentRequirementInline]
    form = RequirementForm

class VersionRangeAdmin(ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    fields = ('name', 'minimum', 'minimum_is_inclusive', 'maximum', 'maximum_is_inclusive')
    search_fields = ('name',)
    ordering = ('name',)
    can_delete = False
    form = VersionRangeForm

class VersionSpecificationAdmin(ModelAdmin):
    list_display = ('__unicode__', 'version', 'version_range')
    list_display_links = ('__unicode__',)
    fields = ('version', 'version_range')
    raw_id_fields = ('version', 'version_range')
    search_fields = ('version__name', 'version_range__name')
    can_delete = False

# register them all

for model in [requirement.EnvironmentRequirement,
              requirement.PackageSpecification, requirement.Requirement,
              requirement.VersionRange, requirement.VersionSpecification]:
    register(model, locals())

# eof
