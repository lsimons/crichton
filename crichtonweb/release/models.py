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

from core.introspection_rules import add_rules
add_rules()

class ReleaseManager(models.Manager):
    def get_by_natural_key(self, product_name, version):
        return self.get(product__name=product_name, version=version)

class Release(crichtonModel):
    objects = ReleaseManager()
    product = models.ForeignKey('prodmgmt.Product', related_name="releases")
    release_order = models.IntegerField(help_text="Determines the ordering for this release related to others.")
    version = models.CharField(max_length=128,
            help_text="How you identify this release. Each release for a product must have a distinct version.")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False, help_text="Deleted releases are hidden from most views and cannot be deployed.")
    
    class Meta:
        app_label = "release"
        unique_together = (('product', 'release_order'),('product', 'version'))
        ordering = ('product', 'release_order')

    def __unicode__(self):
        return "%s %s" % (self.product.name, self.version)
        
    def natural_key(self):
        return (self.product.name, self.version)
    natural_key.dependencies = ['prodmgmt.product']
    
    def product_url(self):
        return '<a href="/admin/prodmgmt/product/%s">%s</a>' % (
                self.product.id, self.product.name)
    product_url.short_description = "Product"
    product_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/release/one/%s@%s.%s" % (self.product.name, self.version, suffix)

    def is_auto_deployable(self):
        """
        Is this release capable of being auto-deployed?
        """
        # If a release element does not have an application configured, then we cannot autodeploy
        # since we don't know the roles->pools->nodes chain.
        for elem in self.elements.all():
            if elem.application is None:
                return False
        return True
    
class ReleaseElementManager(models.Manager):
    def get_by_natural_key(self, product_name, release_version, package_name):
        return self.get(release__product__name=product_name,
            release__version=release_version, package__name=package_name)

class ReleaseElement(crichtonModel):
    objects = ReleaseElementManager()
    release = models.ForeignKey('Release', related_name="elements")
    package = models.ForeignKey('package.Package')
    application = models.ForeignKey('prodmgmt.Application', null=True, blank=True)
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "release"
        unique_together = ('release', 'package')

    def __unicode__(self):
        return "%s: %s %s" % (self.package.name, self.release.product.name,
                self.release.version)
    
    def natural_key(self):
        return (self.release.product.name, self.release.version, self.package.name)
    natural_key.dependencies = ['prodmgmt.product', 'release.release', 'package.packagename']
    
    def application_url(self):
        if self.application:
            return '<a href="/admin/prodmgmt/application/%s">%s</a>' % (
                    self.application.id,self.application.name)
        else:
            return '(None)'
    application_url.short_description = "Application"
    application_url.allow_tags = True

    def get_api_url(self, suffix):
        PRODUCT_NAME="TBD"
        return "/api/release_element/one/%s:%s@%s.%s" % \
               (self.package.name, PRODUCT_NAME,
                self.release.version, suffix)
    
class DeploymentRequestManager(models.Manager):
    def get_by_natural_key(self, product_name, release_version, environment_name):
        return self.get(release__product__name=product_name, release__version__name=release_version,
                environment__name=environment_name)

class DeploymentRequest(crichtonModel):
    objects = DeploymentRequestManager()
    release = models.ForeignKey('Release', related_name="deployment_requests")
    environment = models.ForeignKey('system.Environment', related_name="deployment_requests")
    ops_issue = models.ForeignKey('issue.Issue', related_name="+", blank=True, null=True)
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "release"
        unique_together = ("release", "environment")
    
    def __unicode__(self):
        return "%s->%s" % ( \
                self.release and unicode(self.release), \
                self.environment and self.environment.name or 'unknown-environment')
    
    def natural_key(self):
        return (self.release.product.name, self.release.version, self.environment.name)
    natural_key.dependencies = ['prodmgmt.product', 'release.release', 'system.environment']
    
    def release_url(self):
        return '<a href="/admin/release/release/%s">%s</a>' % (
                self.release.id, unicode(self.release))
    release_url.short_description = "Release"
    release_url.allow_tags = True
    
    def environment_url(self):
        return '<a href="/admin/system/environment/%s">%s</a>' % (
                self.environment.id, self.environment.name)
    environment_url.short_description = "Environment"
    environment_url.allow_tags = True
    
    def ops_issue_url(self):
        if self.ops_issue:
            return '<a href="/admin/issue/issue/%s">%s</a>' % (
                    self.ops_issue.id, self.ops_issue.name)
        else:
            return ''
    ops_issue_url.short_description = "OPS Issue"
    ops_issue_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/deployment_request/one/%s@%s:%s.%s" % \
               (self.release.product.name, self.release.version,
                self.environment.name, suffix)

# eof
