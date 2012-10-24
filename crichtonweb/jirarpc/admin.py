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

from crichtonweb.admin import mysite, ModelAdmin
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.core.register import register
from crichtonweb.issue.models import ISSUETRACKER_TYPE_JIRA
from crichtonweb.release.models import DeploymentRequest
from crichtonweb.release.admin import DeploymentRequestAdmin
from crichtonweb.jirarpc.models import IssueType, CustomField
from crichtonweb.jirarpc.forms import JiraError, JiraDeploymentRequestForm

class IssueTypeAdmin(ModelAdmin):
    list_display = ('name', 'jira_id')
    list_filter = ('name', 'jira_id')

class CustomFieldAdmin(ModelAdmin):
    list_display = ('name', 'jira_name', 'type', 'order')
    list_filter = ('name', 'jira_name', 'type')

class JiraDeploymentRequestAdmin(DeploymentRequestAdmin):
    """Replaces the standard DeploymentRequestAdmin that is used to edit 
    and create deployment requests. This class adds several custom fields
    and sets the form to JiraDeploymentRequestForm.

    """
    fields = DeploymentRequestAdmin.fields
    for custom_field in CustomField.objects.exclude(name='environment').order_by('order'):
        fields.append(custom_field.name)
    # Finally, force 'deleted' to the bottom
    fields.append(fields.pop(fields.index('deleted')))

    form = JiraDeploymentRequestForm

    def save_form(self, request, form, change):
        """Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.

        The difference between this and ModelAdmin.save_form() is that we
        pass the request object in so that the save function can use the 
        Message system.
        """
        return form.save(commit=False, request=request)

    def add_view(self, request, form_url='', extra_context=None):
        """save() has no way to return an error status, so instead we call
        it and catch RemoteJira exceptions which prevent the object being
        saved.

        """
        try:
            return super(JiraDeploymentRequestAdmin, self).add_view(request, form_url, extra_context)
        except JiraError, error:
            messages.error(request, error)
            return HttpResponseRedirect("../jira_error")

    def change_view(self, request, object_id, extra_context=None):
        """save() has no way to return an error status, so instead we call
        it and catch RemoteJira exceptions which prevent the object being
        saved.

        """
        try:
            return super(JiraDeploymentRequestAdmin, self).change_view(request, object_id, extra_context)
        except JiraError, error:
            messages.error(request, error)
            return HttpResponseRedirect("../jira_error")

register(IssueType, locals())
register(CustomField, locals())
if settings.DEPLOYMENTREQUEST_EXTENSION == ISSUETRACKER_TYPE_JIRA:
    mysite.register(DeploymentRequest, JiraDeploymentRequestAdmin)

