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
from django.conf import settings

from crichtonweb.admin import mysite
import crichtonweb.release.models as release
from crichtonweb.core.register import register
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.release.forms import ReleaseForm, ReleaseElementForm, DeploymentRequestForm
import crichtonweb.release.admin_inline as release_inline

class DeploymentRequestAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'release_url', 'environment_url', 'ops_issue_url', 'deleted')
    list_display_links = ('__unicode__',)

    fields = ['release', 'environment', 'ops_issue', 'deleted']

    list_filter = ('deleted', 'environment')
    search_fields = ('release__product__name', 'release__version', 'environment__name',
            'ops_issue__name')
    form = DeploymentRequestForm

class ReleaseAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'release_order', 'deleted')
    list_display_links = ('__unicode__',)
    fields = ('product', 'version', 'release_order', 'rpms', 'is_auto_deployable', 'deleted')
    list_filter = ('deleted',)
    search_fields = ('product__name', 'version')
    list_editable = ('release_order',)
    inlines = [release_inline.ReleaseElementInline]
    form = ReleaseForm
    readonly_fields = ('is_auto_deployable', )
    
class ReleaseElementAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'application_url', 'deleted')
    list_display_links = ('__unicode__',)
    fields = ('release', 'package', 'application', 'deleted')
    list_filter = ('deleted',)
    search_fields = ('release__product__name', 'release__version', 'package__name',
            'application__name')
    form = ReleaseElementForm

# register them all

for model in [release.Release, release.ReleaseElement]:
    register(model, locals())

# Only register the DeploymentRequest admin here if we don't have a 
# specific issue tracker specified. (registration for DeploymentRequest
# would happen elsewhere if that were the case)
if not settings.DEPLOYMENTREQUEST_EXTENSION:
    register(release.DeploymentRequest, locals())

# eof
