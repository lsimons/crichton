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
"""This class implements a few methods for accessing Jira using SOAP.

For connection details and what variables need to be set, see 
soapconnector.py
"""

import logging
import string
from suds import WebFault
from urllib import urlencode
from django.conf import settings
from django.utils import simplejson

from jirarpc import soapconnector
from core.httpshelpers import makeHttps, ok

class JiraHttpsError(Exception): pass

class RemoteJira:
    def __init__(self):
        self.jira = None
        self.auth = None

    @staticmethod
    def get_username_from_email(email):
        """Mimic functionality in the custom jira module which translates
        email address into usernames.

        From the docs: Jira 3 used "the bit of an email address that falls 
        before the @ sign". This code has been changed (because it allows 
        duplicates) and the process is now "the whole email address".

        So we'll just return the email as is. Any older usernames will
        get caught when trying to create issues and code will have to 
        translate the username using get_old_style_username()
        """
        return email

    def get_old_style_username(self, username):
        """Old non-bbc usernames were made up with the bit before the @ only"""
        name, domain = string.split(username, "@")
        return name


    def init_soap(self, force_login=False):
        """Connects to a remote server and stores the Client object 
        as well as the auth token. This is not done be default any more
        since not all calls use SOAP.

        Use force_login=True to force a new auth token.
        """
        if not self.jira:
            self.jira = soapconnector.get_client()
        if not self.auth or force_login:
            self.auth = self.jira.service.login(settings.JIRA_USER, settings.JIRA_PASS)

    def init_https(self):
        """Sets up a new httplib2 Http object for making calls to Jira's
        REST API.

        """
        self.https = makeHttps(url=settings.JIRA_REST_ROOT, 
            cert_file=settings.SSL_CERT_FILE, key_file=settings.SSL_KEY_FILE, 
            ca_file=settings.CA_CERT_FILE)

    def do_https_call(self, uri, method, data=None, content_type='application/x-www-form-urlencoded'):
        """Make a https call to Jira. Returns a (response, content) tuple.

        On failure raises a JiraHttpsError exception.

        """
        self.init_https()
        if content_type == 'application/x-www-form-urlencoded':
            data = urlencode(data)
        response, content = self.https.request(uri, method, data, headers={'Content-Type': content_type})
        if not ok(response):
            logger = logging.getLogger(__name__)
            logger.error("Status code %d returned from '%s' with data '%s'. Content follows: \n%s" % (response.status, uri, data, content))
            raise JiraHttpsError(content)
        return response, content

    def do_rest_call(self, path, method, data):
        """Make a REST API call to Jira. Returns a (response, content) tuple."""
        post_data = simplejson.dumps(data)
        uri = settings.JIRA_REST_ROOT + path
        return self.do_https_call(uri, method, data, 'application/json')


    def add_comment(self, issue_name, comment):
        """Adds a comment to the specified ticket."""
        self.init_soap()
        return self.jira.service.addComment(self.auth, issue_name, comment)

    def create_issue(self, fields):
        """Creates an issue and returns it."""
        # We need to do a little extra handling here - SOCOM-354
        # It's possible to set the 'reporter' field to somebody else
        # but if their email is for an old-style Jira username then it
        # will fail and we need to translate that username into an old-style
        # one.
        # It's a bit nasty calling create_issue twice but it won't happen for 
        # all users and issues are not created that often for it to be a real 
        # problem.
        self.init_soap()
        try:
            new_issue = self.jira.service.createIssue(self.auth, fields)
        except WebFault, err:
            if fields.has_key('reporter') and err.fault.faultstring.find('reporter=The reporter specified is not a user') >= 0:
                fields['reporter'] = self.get_old_style_username(fields['reporter'])
                new_issue = self.jira.service.createIssue(self.auth, fields)
            else:
                raise
        return new_issue

    def get_issue(self, issue_name):
        """Returns the raw data structure for a given issue_name."""
        self.init_soap()
        return self.jira.service.getIssue(self.auth, issue_name)

    def get_issue_types_for_project(self, project):
        """Returns the issue types for this project. Useful because functions 
        like create_issue expect a numeric issue_type.

        """
        self.init_soap()
        return self.jira.service.getIssueTypesForProject(self.auth, project)

    def get_projects(self):
        """Returns the list of projects."""
        self.init_soap()
        return self.jira.service.getProjectsNoSchemes(self.auth)

    def update_issue(self, issue_name, fields):
        """Updates an issue with the provided fields.

        Please note that the format of fields{} is different from the one 
        used to create issues.
        """
        self.init_soap()
        return self.jira.service.updateIssue(self.auth, issue_name, fields)

    def link_issues(self, from_issue, to_issue, link_type, **kwargs):
        """Link two issue together using the provided type. The link_type
        should be the string as it appears in Jira e.g. "is related to"

        This is not possible using soap or xmlrpc. It is possible using the 
        REST api in Jira >= 4.2 but until then we are stuck with doing a simple
        GET.

        The optional kwarg 'from_issue_id' will make this call faster, but
        it will work without.

        """
        # Below is what we would do if the REST api worked.
        # Keeping it here in case we upgrade at some point.
        # data = {
        #    "linkType": link_type,
        #     "fromIssueKey": from_issue,
        #     "toIssueKey": to_issue
        # }
        # response, content = self.do_rest_call("issueLink", "POST", data)
        # Ignore response and content, failure would mean an exception by now
        if kwargs.has_key('from_issue_id'):
            from_issue_id = kwargs['from_issue_id']
        else:
            from_issue_data = self.get_issue(from_issue)
            from_issue_id = from_issue_data['id']
        uri = settings.JIRA_BASE_URL + "secure/LinkExistingIssue.jspa"
        post_data = { "id": from_issue_id,
                 "linkDesc": link_type,
                 "linkKey": to_issue
               }
        self.do_https_call(uri=uri, method="POST", data=post_data)
        # Ignore response and content, failure would mean an exception by now

