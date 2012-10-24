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

import crichtonweb.issue.models as issue
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.core.register import register
import crichtonweb.issue.admin_inline as issue_inline

class IssueAdmin(AuditedAdmin):
    model = issue.Issue
    list_display = ('name', 'summary', 'project_url', 'issue_tracker_url', 'deleted')
    list_display_links = ('name',)
    list_filter = ('deleted','project')
    fields = ('name', 'summary', 'project', 'deleted')
    search_fields = ('name', 'summary', 'project__name')

class IssueTrackerAdmin(AuditedAdmin):
    list_display = ('name', 'display_name', 'tracker_type', 'url_as_url', 'project_list_urls', 'deleted')
    list_display_links = ('name', 'display_name')
    list_filter = ('deleted',)
    fields = ('display_name', 'name', 'tracker_type', 'url',
            'issue_url_pattern', 'deleted')
    prepopulated_fields = {"name": ("display_name",)}
    search_fields = ('name', 'display_name')
    inlines = [issue_inline.IssueTrackerProjectInline]
    
class IssueTrackerProjectAdmin(AuditedAdmin):
    list_display = ('name', 'display_name', 'issue_tracker_url', 'deleted')
    list_display_links = ('name', 'display_name')
    list_filter = ('deleted',)
    fields = ('display_name', 'name', 'issue_tracker', 'deleted')
    prepopulated_fields = {"name": ("display_name",)}
    search_fields = ('name', 'display_name', 'issue_tracker__name')
    # takes too long inlines = [issue_inline.IssueInline]


# register them all

for model in [issue.IssueTracker, issue.IssueTrackerProject, issue.Issue]:
    register(model, locals())

# eof
