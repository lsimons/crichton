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
# example that you can run on mac:
# ./crichton.py indexjiraproject forge-jira https://jira.dev.domain.com/ PIPELINE \
#     --cert-file=/Users/$USER/.bbc/dev.domain.com.pem \
#     --key-file=/Users/$USER/.bbc/dev.domain.com.key \
#     --ca-file=/Users/$USER/.bbc/ca.pem

from optparse import make_option

import xml.sax

from django.core.management.base import CommandError
from django.db import transaction
from django.utils.encoding import iri_to_uri

from crichtoncli.apihelpers import *
from crichtoncli.commands import ApiCommand
from crichtonweb.core.httpshelpers import *
from crichtonweb.issue.models import Issue, IssueTrackerProject, IssueTracker
from crichtonweb.system.models import crichtonCronJobStatus

import logging
logger = logging.getLogger(__name__)

def fetch_issues(jira_client, jirabaseurl, project):
    logger.info("Getting list of issues for %s", project.name)
    issue_list_url = "%ssr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+=+%s+ORDER+BY+key+ASC&tempMax=1000000&field=key&field=summary" % (jirabaseurl, project.name)
    resp, content = jira_client.request(iri_to_uri(issue_list_url), "GET")
    expect_ok(resp, content)
    expect_xml(resp, content)
    
    # note we kinda need to use SAX here because 40k issues in RSS form becomes many MBs of a DOM or Minidom tree....
    # ...we could use lxml but it would add another library dependency that we don't really need
    
    def do_ensure_issue(key, summary):
        issue, created = Issue.objects.ensure(project, key, summary)
        if created:
            logger.info("  added issue %s", key)
    
    class XmlHandler(xml.sax.ContentHandler):
        processing_key = False
        processing_summary = False
        processing_item = False
        
        chars = ""
        key = ""
        summary = ""
        
        def startElement(self, name, attrs):
            if self.processing_key:
                msg = "Unexpected <key/> nested inside <key/>, cannot parse this XML"
                logger.error(msg)
                raise Exception(msg)
            if self.processing_summary:
                msg = "Unexpected <summary/> nested inside <summary/>, cannot parse this XML"
                logger.error(msg)
                raise Exception(msg)
            if name == "key":
                self.processing_key = True
            if name == "summary":
                self.processing_summary = True
            if name == "item":
                self.key = ""
                self.summary = ""
        
        def characters(self, content):
            if self.processing_key or self.processing_summary:
                self.chars += content
        
        def endElement(self, name):
            if name == "key" and self.processing_key:
                self.key = self.chars.strip()
                self.chars = ""
                self.processing_key = False
            
            if name == "summary" and self.processing_summary:
                self.summary = self.chars.strip()
                self.chars = ""
                self.processing_summary = False
            
            if name == "item":
                if self.key and self.summary:
                    do_ensure_issue(self.key, self.summary)
                else:
                    msg = "Found end of item but haven't got both key and summary"
                    logger.error(msg)
                    raise Exception(msg)
                self.key = ""
                self.summary = ""
                self.chars = ""
    xml.sax.parseString(content, XmlHandler())
    

class Command(ApiCommand):
    help = ("Crawl a jira project and add info on all"
            "issues it contains to the crichton db."
            " Can only run locally.")
    args = "<jiraname> <jirabaseurl> <projectname>"

    # option_list = ApiCommand.option_list + (
    # )
    
    # uses database!
    requires_model_validation = True
    
    def print_help(self, jiraname, jirabaseurl, projectname):
        super(ApiCommand, self).print_help(jiraname, jirabaseurl, projectname)
    
    def handle(self, *args, **options):
        if len(args) < 3:
            raise CommandError(
                    "You must provide at least jiraname and jirabaseurl and projectname")
        
        jiraname = args[0]
        jirabaseurl = args[1]
        if not jirabaseurl.endswith("/"):
            jirabaseurl += "/"
        projectname = args[2]
        jira_client = makeHttps(jirabaseurl, **options)
        
        issue_tracker, created = IssueTracker.objects.ensure_jira(jiraname, jirabaseurl)
        project, created = IssueTrackerProject.objects.ensure(issue_tracker, projectname)
        
        fetch_issues(jira_client, jirabaseurl, project)
        crichtonCronJobStatus.objects.update_success('index_jira_project')
