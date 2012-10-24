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
"""This class is used to generate the data structure necessary to create or 
update Jira issues using the RemoteJira class.
"""

from jirarpc.models import CustomField, IssueType

CUSTOMFIELDS = "customFieldValues"
CUSTOMFIELD_NAME = "customfieldId"
CUSTOMFIELD_VALUES = "values"

class IssueBuilder:
    def __init__(self, project, issue_type_name, test_mode=False):
        """Start with blank ticket, and string version of issue_type."""
        self.fields = {}
        self.fields["project"] = project
        if test_mode:
            self.fields["type"] = 1
        else:
            try:
                type_id = IssueType.objects.get(name=issue_type_name).jira_id
            except IssueType.DoesNotExist:
                raise Exception("No type matching '%s' found in IssueType model." % issue_type_name)
            self.fields["type"] = type_id

    def add_custom_field(self, field_name, field_value, test_mode=False):
        """Uses a friendly field name e.g. "Service Picker" to set a field. 
        This is translated into what Jira expects like customfield_10254

        Remember to use field names exactly as they appear in Jira.

        """
        if test_mode:
            jira_name = field_name
        else:
            try:
                jira_name = CustomField.objects.get(name=field_name).jira_name
            except CustomField.DoesNotExist:
                raise Exception("No field matching '%s' found in CustomField model." % field_name)
        # Custom fields need to be inside a list, but make sure that when we're
        # passed an existing list we don't put it inside yet another list
        if not isinstance(field_value, list):
            field_value = [field_value]
        # Check if we are updating or creating new
        already_exists = False
        if self.fields.has_key(CUSTOMFIELDS):
            for loop_field in self.fields[CUSTOMFIELDS]:
                if loop_field[CUSTOMFIELD_NAME] == jira_name:
                    loop_field[CUSTOMFIELD_VALUES] = field_value
                    already_exists = True
                    break
        else:
            self.fields[CUSTOMFIELDS] = []
        if not already_exists:
            custom_field = { CUSTOMFIELD_NAME: jira_name, CUSTOMFIELD_VALUES: field_value }
            self.fields[CUSTOMFIELDS].append(custom_field)

    def add_field(self, field_name, field_value):
        """Sets a plain Jira field by name e.g. 'summary'"""
        self.fields[field_name] = field_value

    def get_issue_create_fields(self):
        """Returns a data structure which can be used to create an issue"""
        return self.fields

    def get_issue_update_fields(self):
        """Returns a data structure which can be used to update an issue"""
        # Need to do a little data munging here:
        # The entire structure is pretty flat, so custom fields are at the 
        # same level as normal fields.
        # Also, every field must be an array
        update_fields = []
        for field_name, field_val in self.fields.iteritems():
            if field_name in ("type", "project"):
                # These are automatically put in when creating IssueBuilder
                # but we don't want to change them
                continue
            if field_name == CUSTOMFIELDS:
                for custom in field_val:
                    to_add = { "id": custom[CUSTOMFIELD_NAME], 
                               "values": custom[CUSTOMFIELD_VALUES] }
                    update_fields.append(to_add)
            else:
                to_add = { "id": field_name, "values": [field_val] }
                update_fields.append(to_add)
        return update_fields

