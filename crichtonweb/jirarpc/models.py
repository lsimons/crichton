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
from django.db import models
from crichtonweb.core.models import crichtonModel

from audit_log.models.managers import AuditLog

class IssueType(crichtonModel):
    name = models.CharField(max_length=45, primary_key=True)
    jira_id = models.IntegerField()
    audit_log = AuditLog()

    class Meta:
        app_label = "jirarpc"
        ordering = ('name',)

    def __unicode__(self):
        return self.name

CUSTOM_FIELD_TYPES = (
    ('date', 'DateTime'),
    ('char', 'CharField'),
    ('text', 'TextBox'),
    ('drop', 'Select'),
    ('mult', 'MultipleSelect')
)

class CustomField(crichtonModel):
    name = models.CharField(max_length=45, primary_key=True)
    jira_name = models.CharField(max_length=30)
    type = models.CharField(max_length=4, choices=CUSTOM_FIELD_TYPES, default='char')
    default = models.CharField(max_length=40, blank=True, default='')
    choices = models.TextField(blank=True, default='')
    helptext = models.TextField(blank=True, default='')
    required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    audit_log = AuditLog()

    class Meta:
        app_label = "jirarpc"
        ordering = ('name',)

    def __unicode__(self):
        return self.name
