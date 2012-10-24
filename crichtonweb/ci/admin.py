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
from crichtonweb.admin import mysite
import crichtonweb.ci.models as ci
import crichtonweb.ci.admin_inline as ci_inline
from crichtonweb.core.register import register
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.admin.options import ModelAdmin
from crichtonweb.ci.forms import BuildJobForm, BuildResultForm

#
# Admins
#

class BuildJobAdmin(AuditedAdmin):
    list_display = ('name', 'build_server_url', 'product_url', 'deleted')
    list_display_links = ('name',)
    list_filter = ('deleted', 'build_server')
    fields = ('name', 'build_server', 'product', 'deleted')
    search_fields = ('name', 'build_server__name', 'product__name')
    # takes too long inlines = [BuildResultInline]
    form = BuildJobForm

class BuildResultAdmin(ModelAdmin):
    list_display = ('__unicode__', 'job_url', 'build_number', 'succeeded', 'finished_at', 'produced_package_url', 'deleted')
    list_display_links = ('__unicode__', 'build_number')
    list_filter = ('succeeded', 'deleted')
    date_hierarchy = 'finished_at'
    fields = ('job', 'build_number', 'succeeded', 'finished_at', 'produced_package', 'deleted', 'log')
    search_fields = ('job__name', 'build_number', 'produced_package__name')
    form = BuildResultForm

class BuildServerAdmin(AuditedAdmin):
    list_display = ('name', 'display_name', 'build_server_type', 'url_as_url', 'deleted')
    list_display_links = ('name', 'display_name')
    list_filter = ('deleted',)
    fields = ('display_name', 'name', 'build_server_type', 'url', 'deleted')
    prepopulated_fields = {"name": ("display_name",)}
    search_fields = ('name', 'display_name')
    # takes too long inlines = [BuildJobInline]


# register them all

for model in [ci.BuildServer, ci.BuildJob, ci.BuildResult]:
    register(model, locals())

# eof
