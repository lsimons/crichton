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
from django import template
from django.conf import settings

from crichtonweb.jirarpc.models import CustomField

register = template.Library()

class CustomDateListNode(template.Node):
    """Return a list of customfields that are dates."""
    def __init__(self, var_name):
        self.var_name = var_name
    def render(self, context):
        context[self.var_name] = CustomField.objects.exclude(name='environment').filter(type='date')
        return ''

@register.tag
def get_custom_date_fields(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return CustomDateListNode(var_name)

class JiraSettingsNode(template.Node):
    """Return a list of settings related to Jira:
    - JIRA_BASE_URL
    - OPS_PROJECT_NAME
    - JIRA_USER

    I considered making this a more general purpose 'send all settings to the 
    template' but I'm not sure if that's a good idea because
    a) probably not needed anywhere else
    b) sensitive info like passwords in there

    """
    def __init__(self, var_name):
        self.var_name = var_name
    def render(self, context):
        context[self.var_name] = {
            'JIRA_BASE_URL': settings.JIRA_BASE_URL,
            'OPS_PROJECT_NAME': settings.OPS_PROJECT_NAME,
            'JIRA_USER': settings.JIRA_USER,
        }
        return ''

@register.tag
def get_jira_settings(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return JiraSettingsNode(var_name)
