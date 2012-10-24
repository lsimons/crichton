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
from django.db import models
from crichtonweb.core.models import crichtonModel

from audit_log.models.managers import AuditLog

from core.utils import commit_or_rollback
from core.introspection_rules import add_rules
add_rules()

ISSUETRACKER_TYPE_JIRA = 'jira'

#
# Issue
#

class IssueManager(models.Manager):
    def get_by_natural_key(self, name, project_name, issue_tracker_name):
        return self.get(name=name, project__name=project_name,
                project__issue_tracker__name=issue_tracker_name)
    
    @commit_or_rollback
    def ensure(self, issue_tracker_project, issue_name, issue_summary):
        issue, created = self.get_or_create(project=issue_tracker_project, name=issue_name)
        if created or issue.summary != issue_summary or issue.deleted:
            issue.summary = issue_summary
            issue.deleted = False
            issue.save()
        return issue, created

class PipelineIssueManager(IssueManager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(project__name="PIPELINE")
    
class OpsIssueManager(IssueManager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(project__name=settings.OPS_PROJECT_NAME)

class Issue(crichtonModel):
    objects = IssueManager()
    pipeline = PipelineIssueManager()
    ops = OpsIssueManager()
    
    name = models.SlugField(max_length=128,
            help_text="Unique name or id for the issue in its issue tracker.")
    summary = models.CharField(max_length=255, default="",
                               help_text="Summary of issue from its issue tracker.")
    project = models.ForeignKey('IssueTrackerProject', related_name="issues")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "issue"
        unique_together = ("name", "project")
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def longname(self):
        return "%s: %s" % (self.name, self.summary)
    
    def get_api_url(self, suffix):
        return "/api/issue/one/%s:%s@%s.%s" % (self.project.name, self.name,
                                             self.project.issue_tracker.name,
                                               suffix)

    def natural_key(self):
        return (self.name, self.project.name, self.project.issue_tracker.name)
    natural_key.dependencies = ['issue.issuetrackerproject']

    def project_url(self):
        return '<a href="/admin/issue/issuetrackerproject/%s">%s</a>' % (
                self.project.id, self.project.name)
    project_url.short_description = "Project"
    project_url.allow_tags = True
    
    def issue_tracker_url(self):
        return '<a href="/admin/issue/issuetracker/%s">%s</a>' % (
                self.project.issue_tracker.id, self.project.issue_tracker.name)
    issue_tracker_url.short_description = "Issue Tracker"
    issue_tracker_url.allow_tags = True
    
    def remote_url(self):
        pattern = self.project.issue_tracker.issue_url_pattern
        if not pattern:
            return ""
        ctx = {
            "issue_id": self.name,
        }
        return pattern % ctx
    
#
# IssueTracker
#

class IssueTrackerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
    @commit_or_rollback
    def ensure_jira(self, jiraname, jirabaseurl):
        issue_tracker, created = self.get_or_create(name=jiraname)
        # Only save if we're about to change data or it goes into the audit log
        if created or issue_tracker.deleted or \
                issue_tracker.tracker_type != ISSUETRACKER_TYPE_JIRA or \
                issue_tracker.url != jirabaseurl or \
                issue_tracker.issue_url_pattern != jirabaseurl + "browse/%(issue_id)s":
            issue_tracker.name = jiraname
            issue_tracker.tracker_type = ISSUETRACKER_TYPE_JIRA
            issue_tracker.url = jirabaseurl
            issue_tracker.issue_url_pattern = jirabaseurl + "browse/%(issue_id)s"
            issue_tracker.deleted = False
            issue_tracker.save()
        return issue_tracker, created
    
    def ensure_from_config(self):
        return self.ensure_jira(settings.JIRA_NAME, settings.JIRA_BASE_URL)

class IssueTracker(crichtonModel):
    objects = IssueTrackerManager()
    ISSUE_TRACKER_TYPES = (
        (ISSUETRACKER_TYPE_JIRA, 'Jira'),
    )
    name = models.SlugField(max_length=128, unique=True,
            help_text="Uniquely identifies the issue tracker. Used in URLs.")
    display_name = models.CharField(max_length=200, blank=True,
            help_text="Human-readable name for the issue tracker.")
    tracker_type = models.CharField(max_length=12, choices=ISSUE_TRACKER_TYPES,
            default=ISSUETRACKER_TYPE_JIRA)
    url = models.URLField(max_length=255, blank=True, verify_exists=False,
            help_text="URL for users to access this issue tracker.")
    issue_url_pattern = models.URLField(max_length=255, blank=True, verify_exists=False,
            help_text="URL pattern for how issues are accessed in this tracker." +
            " The string %(issue_id)s will be replaced by the issue id.")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "issue"
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)
    
    def url_as_url(self):
        return '<a href="%s">%s</a>' % (self.url,self.url)
    url_as_url.short_description = "URL"
    url_as_url.allow_tags = True
    
    def project_list_urls(self):
        qs = self.projects.filter(deleted=False)
        return ", ".join(['<a href="/admin/issue/issuetrackerproject/%s">%s</a>' % (
                p.id, p.name) for p in qs])
    project_list_urls.short_description = "Projects"
    project_list_urls.allow_tags = True
    
    def get_api_url(self, suffix):
        return "/api/issue_tracker/one/%s.%s" % (self.name, suffix)
    
#
# IssueTrackerProject
#

class IssueTrackerProjectManager(models.Manager):
    def get_by_natural_key(self, name, issue_tracker_name):
        return self.get(name=name, issue_tracker__name=issue_tracker_name)
    
    @commit_or_rollback
    def ensure(self, issue_tracker, projectname):
        project, created = self.get_or_create(issue_tracker=issue_tracker,
                name=projectname)
        project.undelete()
        return project, created

class IssueTrackerProject(crichtonModel):
    objects = IssueTrackerProjectManager()
    name = models.SlugField(max_length=128,
            help_text="Unique name or id for the project in its issue tracker.")
    display_name = models.CharField(max_length=200, blank=True,
            help_text="Human-readable name for the project.")
    issue_tracker = models.ForeignKey('IssueTracker', related_name="projects")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "issue"
        unique_together = ("name", "issue_tracker")
        ordering = ('name',)

    def __unicode__(self):
        return self.name + '@' + \
                (self.issue_tracker and self.issue_tracker.name or 'unnamed-tracker')
    
    def natural_key(self):
        return (self.name, self.issue_tracker.name)
    natural_key.dependencies = ['issue.issuetracker']
    
    def get_api_url(self, suffix):
        return "/api/issue_tracker_project/one/%s@%s.%s" % (self.name, self.issue_tracker.name, suffix)
    
    def issue_tracker_url(self):
        return '<a href="/admin/issue/issuetracker/%s">%s</a>' % (
                self.issue_tracker.id, self.issue_tracker.name)
    issue_tracker_url.short_description = "Issue Tracker"
    issue_tracker_url.allow_tags = True
    
# eof
