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
import datetime
import logging
import string
import time
import traceback

from django import forms
from django.contrib import messages
from django.forms import ModelForm, ModelChoiceField
from django.forms.models import ModelFormMetaclass
from django.db import models
from django.forms.widgets import *
from django.conf import settings

from ajax_select.fields import AutoCompleteSelectField

from crichtonweb.core.widgets import force_readonly, crichtonTextarea
from crichtonweb.issue.models import Issue, IssueTracker, IssueTrackerProject
from crichtonweb.jirarpc import IssueBuilder, RemoteJira
from crichtonweb.jirarpc.models import CustomField
from crichtonweb.release.models import DeploymentRequest, Release, ReleaseElement
from crichtonweb.release.widgets import SplitSelectDateTimeWidget
from crichtonweb.system.models import Environment


class JiraError(Exception): pass

JIRA_DATE_FORMAT = '%d/%b/%y'
JIRA_DATETIME_FORMAT = '%d/%b/%y %H:%M'

class JiraCustomModelFormMetaclass(ModelFormMetaclass):
    """Meta class that sets up class attributes based on the jirarpc.CustomField model."""
    def __new__(cls, name, bases, classdict):
        for cf in CustomField.objects.exclude(name='environment'):
            field_attrs = {'required': cf.required, 'help_text': cf.helptext, 'initial': cf.default}
            if cf.type == 'char':
                classdict[cf.name] = forms.CharField(widget=forms.TextInput(attrs={'size':'80'}), **field_attrs)
            elif cf.type == 'text':
                classdict[cf.name] = forms.CharField(widget=crichtonTextarea(attrs={'rows':'4', 'cols':'80'}), **field_attrs)
            elif cf.type == 'date':
                classdict[cf.name] = forms.SplitDateTimeField(input_date_formats=[JIRA_DATE_FORMAT], widget=SplitSelectDateTimeWidget(date_format=JIRA_DATE_FORMAT, minute_step=15, twelve_hr=False, show_seconds=False), **field_attrs)
            elif cf.type == 'drop' or cf.type == 'mult':
                choices = []
                for choice in string.split(cf.choices, '|'):
                    choices.append( (choice, choice) )
                if cf.type == 'mult':
                    # Change way 'initial' is passed in
                    field_attrs['initial'] = [cf.default]
                    classdict[cf.name] = forms.MultipleChoiceField(choices=choices, widget=SelectMultiple(attrs={'size':'5'}), **field_attrs)
                else:
                    classdict[cf.name] = forms.ChoiceField(choices=choices, **field_attrs)
            else:
                raise Exception("Unknown custom field type '%s' specified" % cf.type)
        return super(JiraCustomModelFormMetaclass, cls).__new__(cls, name, bases, classdict)

class JiraDeploymentRequestForm(ModelForm):
    __metaclass__ = JiraCustomModelFormMetaclass

    release = AutoCompleteSelectField('release', label='Release')
    ops_issue = AutoCompleteSelectField('ops_issue', required=False, help_text="Leave this blank for crichton to create a ticket in Jira", label='OPS ticket')

    class Meta:
        model = DeploymentRequest

    def __init__(self, *args, **kwargs):
        super(JiraDeploymentRequestForm, self).__init__(*args, **kwargs)

        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            if instance.ops_issue is None:
                # New DeploymentRequest = new jira issue
                # Default values come from model
                pass
            else:
                # Populate custom fields from issue
                jira = RemoteJira()
                issue = jira.get_issue(instance.ops_issue.name)
                rev_custom_fields = {}
                for cf in CustomField.objects.exclude(name='environment'):
                    # Create mapping for custom fields
                    rev_custom_fields[cf.jira_name] = {'name': cf.name, 'type': cf.type}
                for field in issue.customFieldValues:
                    if rev_custom_fields.has_key(field.customfieldId):
                        custom_field = rev_custom_fields[field.customfieldId]
                        if custom_field['type'] == 'date':
                            # Parse DateTime field
                            # self.initial[custom_field['name']] = datetime.strptime(field.values[0], JIRA_DATETIME_FORMAT)
                            # Python 2.4:
                            self.initial[custom_field['name']] = datetime.datetime(*(time.strptime(field.values[0], JIRA_DATETIME_FORMAT)[0:5]))
                        elif custom_field['type'] == 'mult':
                            self.initial[custom_field['name']] = field.values
                        else:
                            self.initial[custom_field['name']] = field.values[0]

    def clean(self):
        """Custom validation"""
        cleaned_data = super(JiraDeploymentRequestForm, self).clean()
   
        for cf in CustomField.objects.exclude(name='environment'):
            if cf.type in ['drop', 'mult']:
                # 'None' in select fields is handled as follows:
                # If the field is optional, treat None as blank and delete the value
                # because Jira rejects the value 'None'
                # If it is a required field and it contains None then leave it alone
                # because that means 'None' was added as just another option.
                if not cf.required and cleaned_data.has_key(cf.name) and ((isinstance(cleaned_data[cf.name], list) and len(cleaned_data[cf.name]) > 0 and cleaned_data[cf.name][0] == 'None') or (cleaned_data[cf.name] == 'None')):
                    # Optional field with value = None, treat as missing
                    del cleaned_data[cf.name]
            elif cf.type == 'text':
                # Ensure we always use line breaks only, or it messes with self.changed_data
                if cleaned_data.has_key(cf.name):
                    cleaned_data[cf.name] = cleaned_data[cf.name].replace("\r", "")
        return cleaned_data

    def _jira_connect(self):
        """Connect to Jira and return the object. On failure log error and raise exception."""
        try:
            return RemoteJira()
        except Exception, err:
            logger = logging.getLogger(__name__)
            logger.error("Error while connecting to Jira. Stack trace follows.\n%s" % traceback.format_exc())
            raise JiraError("Unable to connect to Jira. %s" % err)

    def _make_jira_field(self, field_value):
        """Given a value, returns the string version suitable for sending
        in a Jira SOAP request."""
        if isinstance(field_value, datetime.datetime):
            # Jira only accepts dates in a very specific format
            return field_value.strftime(JIRA_DATETIME_FORMAT)
        elif isinstance(field_value, Environment):
            # Our use of the environment field conflicts with the Jira custom
            # field of the same name. Make sure we send the right text
            return field_value.name.capitalize()
        if isinstance(field_value, list):
            return_list = [self._make_jira_field(x) for x in field_value]
            return return_list
        return field_value

    def save(self, request, commit=True):
        """When saving, first create or update issue in Jira. If necessary 
        store the ticket number in the ops_issue field.

        This method requires the 'request' parameter which differs from the 
        normal ModelForm.save(). Ensure that the admin object overrides 
        form_save() to pass it in.
        """
        model = super(JiraDeploymentRequestForm, self).save(commit=False)
        release = model.release

        # If release_content blank, populate it from release
        if self.cleaned_data['release_content'] == "":
            self.cleaned_data['release_content'] = self.make_rpm_list_from_release(release)
            if self.cleaned_data['release_content'] == "":
                raise Exception("No rpms found for release, can't create Jira issue")

        if model.ops_issue is None:
            # Creating issue
            summary = "Release %s to %s" % (release, self.cleaned_data['environment'])
            issue = IssueBuilder(settings.OPS_PROJECT_NAME, "Change")
            issue.add_field("summary", summary)
            issue.add_field("assignee", "unassigned")
            issue.add_field("reporter", RemoteJira.get_username_from_email(request.user.email))

            # Now loop through all possible custom fields and add to issue
            for field in CustomField.objects.all():
                if not self.cleaned_data.has_key(field.name):
                    continue
                field_value = self._make_jira_field(self.cleaned_data[field.name])
                issue.add_custom_field(field.name, field_value)
            
            remote_jira = self._jira_connect()
            try:
                new_issue = remote_jira.create_issue(issue.get_issue_create_fields())
                issue_name = new_issue["key"]
            except Exception, err:
                logger = logging.getLogger(__name__)
                logger.error("Error while creating Jira issue. Stack trace follows.\n%s" % traceback.format_exc())
                raise JiraError("Error while trying to create Jira issue: %s" % err)

            issue_tracker, created = IssueTracker.objects.ensure_from_config()                
            project, created = IssueTrackerProject.objects.ensure(issue_tracker, settings.OPS_PROJECT_NAME)
            issue, created = Issue.objects.ensure(project, issue_name, summary)

            model.ops_issue = issue
            messages.success(request, "Jira change ticket %s created." % issue_name)

            # Link new ticket to PIPELINE ticket
            pipeline_issue_name = release.product.pipeline_issue.name
            try:
                remote_jira.link_issues(from_issue=issue_name, 
                    to_issue=pipeline_issue_name, link_type="is related to",
                    from_issue_id=new_issue["id"])
            except Exception, err:
                # Don't abort, if the issue was created above then it's OK if it couldn't link
                messages.error(request, "Error while trying to link issues in Jira (The change ticket was still created, it's just not linked to your PIPELINE issue): %s" % err)
        else:
            # Updating existing issue
            issue = IssueBuilder(settings.OPS_PROJECT_NAME, "Change")
            changed_fields = self.changed_data
            if len(changed_fields) > 0:
                custom_field_lookup = [x.name for x in CustomField.objects.all()]
                for changed_field in changed_fields:
                    if not self.cleaned_data.has_key(changed_field):
                        field_value = None
                    else:
                        field_value = self._make_jira_field(self.cleaned_data[changed_field])
                    if changed_field in custom_field_lookup:
                        issue.add_custom_field(changed_field, field_value)
                    else:
                        issue.add_field(changed_field, field_value)

                remote_jira = self._jira_connect()
                try:
                    remote_jira.update_issue(model.ops_issue, issue.get_issue_update_fields())
                except Exception, err:
                    logger = logging.getLogger(__name__)
                    logger.error("Error while updating Jira issue. Stack trace follows.\n%s" % traceback.format_exc())
                    raise JiraError("Error while trying to update Jira issue: %s" % err)
                messages.success(request, "Jira change ticket %s updated." % model.ops_issue)

        if commit:
            model.save()
 
        return model

    def make_rpm_list_from_release(self, release):
        """Return a \n separated list of rpm filenames for a given release."""
        release_elems = ReleaseElement.objects.filter(release=release)
        # TODO: how to get the correct architecture?
        return string.join(['%s.noarch.rpm' % x.package for x in release_elems], "\n")

# eof
