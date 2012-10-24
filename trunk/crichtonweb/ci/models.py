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

from django.db import models

from audit_log.models.managers import AuditLog
from core.fields import CompressedTextField
from crichtonweb.core.models import crichtonModel

from core.utils import commit_or_rollback
from core.introspection_rules import add_rules
add_rules()

class BuildJobManager(models.Manager):
    def get_by_natural_key(self, name, build_server_name):
        return self.get(name=name, build_server__name=build_server_name)

    @commit_or_rollback
    def ensure(self, build_server, name):
        result, created = self.get_or_create(name=name,
                build_server=build_server)
        result.undelete()
        return result, created

class BuildJob(crichtonModel):
    objects = BuildJobManager()
    name = models.CharField(max_length=255,
            help_text="Identifies this job at its build server.")
    build_server = models.ForeignKey('BuildServer', related_name="jobs")
    product = models.ForeignKey('prodmgmt.Product', null=True, blank=True, related_name="build_jobs")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "ci"
        unique_together = ("name", "build_server")
        # takes too long ordering = ('build_server', 'name')
        ordering = ('name',)

    def __unicode__(self):
        return (self.name or 'unnamed') + '@' + \
                (self.build_server and self.build_server.name or 'unnamed-server')
    
    def natural_key(self):
        return (self.name, self.build_server.name)
    natural_key.dependencies = ['ci.buildserver']
    
    def build_server_url(self):
        return '<a href="/admin/ci/buildserver/%s">%s</a>' % (self.build_server.id,self.build_server.name)
    build_server_url.short_description = "Build Server"
    build_server_url.allow_tags = True
    
    def product_url(self):
        return '<a href="/admin/prodmgmt/product/%s">%s</a>' % (self.product.id,self.product.name)
    product_url.short_description = "Product"
    product_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/build_job/one/%s@%s.%s" % (self.name, self.build_server.name, suffix)

class BuildResultManager(models.Manager):
    def get_by_natural_key(self, name, job_name, build_server_name):
        return self.get(name=name, job__name=job_name, \
                job__build_server__name=build_server_name)
    
    @commit_or_rollback
    def ensure(self, build_job, build_number, success, timestamp, log):
        try:
            try:
                result, created = self.get_or_create(job=build_job,
                        build_number=build_number, defaults = {
                            "succeeded": success,
                            "finished_at": timestamp,
                            "log": log,
                        })
            except Warning:
                result, created = self.get_or_create(job=build_job,
                        build_number=build_number, defaults = {
                            "succeeded": success,
                            "finished_at": timestamp,
                            "log": "Log contains bad character data, can't save to database as UTF-8",
                        })
        except IntegrityError, e:
            transaction.rollback()
        result.undelete()
        return result, created

class BuildResult(crichtonModel):
    objects = BuildResultManager()
    build_number = models.IntegerField(
            help_text="Identifies this build within its build job.")
    succeeded = models.BooleanField(default=False)
    finished_at = models.DateTimeField(default = datetime.datetime.now) 
    log = CompressedTextField(null=True,blank=True)
    job = models.ForeignKey('BuildJob', related_name="results")
    produced_package = models.ForeignKey('package.Package',null=True,blank=True,
            related_name="builds")
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "ci"
        unique_together = ("job", "build_number")
        # takes too long ordering = ('job', 'build_number')

    def __unicode__(self):
        return (self.job and self.job.name or 'unnamed-job') + "#" + \
                str(self.build_number) + '@' + \
                (self.job and self.job.build_server and \
                        self.job.build_server.name or 'unnamed-server')
    
    def natural_key(self):
        return (self.name, self.job.name, self.job.build_server.name)
    natural_key.dependencies = ['ci.buildserver', 'ci.buildjob']
    
    def job_url(self):
        return '<a href="/admin/ci/buildjob/%s">%s</a>' % (self.job.id,self.job.name)
    job_url.short_description = "Build job"
    job_url.allow_tags = True
    
    def produced_package_url(self):
        if self.produced_package:
            return '<a href="/admin/package/package/%s">%s</a>' % (self.produced_package.id,self.produced_package.name)
        else:
            return ''
    produced_package_url.short_description = "Produced package"
    produced_package_url.allow_tags = True
    
    def get_api_url(self, suffix):
        return "/api/build_result/one/%s:%s@%s.%s" % (self.job.name, self.build_number, self.job.build_server.name, suffix)

class BuildServerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
    @commit_or_rollback
    def ensure_hudson(self, hudsonname, hudsonbaseurl):
        result, created = self.get_or_create(name=hudsonname,
                build_server_type="hudson",
                defaults={
                        "url": hudsonbaseurl,
                        "build_job_pattern" : hudsonbaseurl + "job/%(job_id)s/"
                })
        if result.url != hudsonbaseurl:
            result.url = hudsonbaseurl
            result.build_job_pattern = hudsonbaseurl + "job/%(job_id)s/"
            result.save()
        result.undelete()
        return result, created

class BuildServer(crichtonModel):
    objects = BuildServerManager()
    BUILD_SERVER_TYPES = (
        ('hudson', 'Hudson'),
    )
    name = models.SlugField(max_length=128, unique=True,
            help_text="Uniquely identifies the build server. Used in URLs.")
    display_name = models.CharField(max_length=200, blank=True,
            help_text="Human-readable name for the build server.")
    build_server_type = models.CharField(max_length=12, choices=BUILD_SERVER_TYPES,
            default='hudson')
    url = models.URLField(max_length=255, blank=True, verify_exists=False,
            help_text="URL for users to access this build server.")
    build_job_pattern = models.URLField(max_length=255, blank=True, verify_exists=False,
            help_text="URL pattern for how to find build jobs in this tracker." +
            " The string %(job_id)s will be replaced by the job id.")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "ci"
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)
    
    def url_as_url(self):
        return '<a href="%s">%s</a>' % (self.url,self.url)
    url_as_url.short_description = "URL"
    url_as_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/build_server/one/%s.%s" % (self.name, suffix)

# eof
