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
import pprint
from django.http import HttpResponse
from django.utils import simplejson

from jirarpc import RemoteJira

def display_issue(request, issue):
    """Fetches and displays an existing issue. Please note that this data 
    can not necessarily be fed straight back into create_issue(). Most
    important difference is in the custom fields:
    display_issue gives you:
    {'customfieldId': 'customfield_10214', 'values': 'No'}
    ...but you need to send:
    {'customfieldId': 'customfield_10214', 'values': ['No']}

    This is for debugging purposes only

    """
    jira = RemoteJira()
    data = jira.get_issue(issue)
    # body = simplejson.dumps(data, indent=4)
    # return HttpResponse(body, content_type="application/json", status=200)
    body = pprint.PrettyPrinter(indent=4).pformat(data)
    return HttpResponse(body, content_type="text/plain", status=200)

def display_issue_types(request, project_id):
    """Displays all issue types for this project.

    This is for debugging purposes only.

    """
    jira = RemoteJira()
    data = jira.get_issue_types_for_project(project_id)
    # body = simplejson.dumps(data, indent=4)
    # return HttpResponse(body, content_type="application/json", status=200)
    body = pprint.PrettyPrinter(indent=4).pformat(data)
    return HttpResponse(body, content_type="text/plain", status=200)

def display_projects(request):
    """Displays all projects (used for getting their IDs)

    This is for debugging purposes only.

    """
    jira = RemoteJira()
    data = jira.get_projects()
    # body = simplejson.dumps(data, indent=4)
    # return HttpResponse(body, content_type="application/json", status=200)
    body = pprint.PrettyPrinter(indent=4).pformat(data)
    return HttpResponse(body, content_type="text/plain", status=200)

