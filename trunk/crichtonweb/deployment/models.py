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
from django.core.exceptions import PermissionDenied, ValidationError

from audit_log.models.managers import AuditLog
from core.fields import CompressedTextField

from crichtonweb.core.models import crichtonModel

from core.utils import commit_or_rollback
from core.introspection_rules import add_rules
add_rules()

class ApplicationDeployment(crichtonModel):
    # only via requirements (?)
    # application = models.ForeignKey(Application, related_name="applications")
    environment = models.ForeignKey('system.Environment', null=True, blank=True,
            related_name="application_deployments")
    pool = models.ForeignKey('system.Pool', null=True, blank=True, related_name="deployments")
    insert_date = models.DateTimeField(default = datetime.datetime.now)
    recipe = models.ForeignKey('deployment.Recipe', related_name="deployments")
    product_deployment = models.ForeignKey('ProductDeployment', null=True,
            related_name="application_deployments")
    # todo requirements
    log = CompressedTextField(null=True,blank=True)
    
    class Meta:
        app_label = "deployment"
        ordering = ('insert_date',)

    def clean(self):
        if self.environment and self.pool:
            raise ValidationError("ApplicationDeployment should point to" +\
                    " either an Environment or a Pool, not both")
        if not self.environment and not self.pool:
            raise ValidationError("ApplicationDeployment should point to" +\
                    " either an Environment or a Pool, none are set")
    
    def delete(self, *args, **kwargs):
        raise PermissionDenied("Deleting information about deployments is not allowed.")
    
    def undelete(self, *args, **kwargs):
        raise PermissionDenied("Deleting information about deployments is not allowed.")
    
    def get_name(self):
        return "%s -> %s" % (self.recipe and self.recipe.name or 'unnamed-recipe',
                             self.environment and self.environment.name or self.pool.name)
    
    def get_date(self):
        return self.insert_date.isoformat()
    
    def get_name_and_date(self):
        return "%s @%s" % (self.get_name(), self.get_date())
    
    def __unicode__(self):
        return self.get_name_and_date()
    
    def environment_url(self):
        return '<a href="/admin/system/environment/%s">%s</a>' % (
                self.environment.id, self.environment.name)
    environment_url.short_description = "Environment"
    environment_url.allow_tags = True
    
    def pool_url(self):
        return '<a href="/admin/system/pool/%s">%s</a>' % (
                self.pool.id, self.pool.name)
    pool_url.short_description = "Pool"
    pool_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/application_deployment/one/%s.%s" % (self.id, suffix)
        
class DeploymentSystemManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
    @commit_or_rollback
    def ensure_hudson(self, hudsonname, hudsonbaseurl):
        result, created = self.get_or_create(name=hudsonname,
                deployment_system_type="hudson",
                defaults={
                        "url": hudsonbaseurl,
                        # todo maybe these should be configurable...
                        "takes_specific_version": False,
                        "takes_specific_pool": False,
                })
        if result.url != hudsonbaseurl:
            result.url = hudsonbaseurl
            result.save()
        result.undelete()
        return result, created

class DeploymentSystem(crichtonModel):
    objects = DeploymentSystemManager()
    DEPLOYMENT_SYSTEM_TYPES = (
        ('puppet', 'Puppet'),
        ('fabric', 'Fabric'),
        ('hudson', 'Hudson'),
    )
    name = models.SlugField(max_length=128, unique=True,
            help_text="Uniquely identifies the deployment system. Used in URLs.")
    display_name = models.CharField(max_length=200, blank=True,
            help_text="Human-readable name for the build server.")
    deployment_system_type = models.CharField(max_length=12, choices=DEPLOYMENT_SYSTEM_TYPES,
            default='puppet')
    url = models.URLField(max_length=255, blank=True, verify_exists=False,
            help_text="URL for users to access this build server.")
    takes_specific_version = models.BooleanField(default=False)
    takes_specific_pool = models.BooleanField(default=False)
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "deployment"
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)
    
    def url_as_url(self):
        return '<a href="%s">%s</a>' % (self.url,self.url)
    url_as_url.short_description = "URL"
    url_as_url.allow_tags = True
    
    def environment_usage_list_urls(self):
        qs = self.environment_usages.filter(deleted=False)
        return ", ".join(['<a href="/admin/deployment/deploymentpreference/%s">%s</a>:'
                '<a href="/admin/system/environment/%s">%s</a>' % (
                dp.id, dp.preference_number, dp.environment.id,
                dp.environment.name) for dp in qs])
    environment_usage_list_urls.short_description = "Environment usage"
    environment_usage_list_urls.allow_tags = True
    
    def get_api_url(self, suffix):
        return "/api/deployment_system/one/%s.%s" % (self.name, suffix)
    
class DeploymentPreferenceManager(models.Manager):
    def get_by_natural_key(self, environment_name, preference_number):
        return self.get(environment_name=environment_name,
                preference_number=preference_number)

class DeploymentPreference(crichtonModel):
    objects = DeploymentPreferenceManager()
    environment = models.ForeignKey('system.Environment', related_name="deployment_preferences")
    deployment_system = models.ForeignKey('DeploymentSystem',
            related_name="environment_usages")
    preference_number = models.SmallIntegerField(default=999,
            help_text="If multiple systems could be used for a deployment" +
            " the one with the smallest preference number is used")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "deployment"
        unique_together = ("environment", "preference_number")
        ordering = ('environment', 'preference_number')

    def __unicode__(self):
        return self.environment.name + ":" + str(self.preference_number) + \
                ":" + self.deployment_system.name
    
    def natural_key(self):
        return (self.environment_name, preference_number)
    
    def environment_url(self):
        return '<a href="/admin/system/environment/%s">%s</a>' % (
                self.environment.id,self.environment.name)
    environment_url.short_description = "Environment"
    environment_url.allow_tags = True
    
    def deployment_system_url(self):
        return '<a href="/admin/system/deploymentsystem/%s">%s</a>' % (
                self.deployment_system.id,self.deployment_system.display_name)
    deployment_system_url.short_description = "Deployment system"
    deployment_system_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/deployment_preference/one/%s_%s.%s" % (self.environment.name, self.preference_number, suffix)
    
class NodeDeployment(crichtonModel):
    application_deployment = models.ForeignKey('ApplicationDeployment',
            related_name="node_deployments")
    node = models.ForeignKey('system.Node', related_name="deployments")
    succeeded = models.BooleanField(default=False)
    started = models.DateTimeField(default = datetime.datetime.now, null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)
    log = CompressedTextField(null=True,blank=True)
    
    class Meta:
        app_label = "deployment"
        ordering = ('started',)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Deleting information about deployments is not allowed.")
    
    def __unicode__(self):
        return "%s: %s -> %s @%s" % (self.id, self.application_deployment.recipe.name,
                self.node.name or 'unknown-node', self.started.isoformat())

    def application_deployment_url(self):
        return '<a href="/admin/system/applicationdeployment/%s">%s</a>' % (
                self.application_deployment.id,unicode(self.application_deployment))
    application_deployment_url.short_description = "Application deployment"
    application_deployment_url.allow_tags = True
    
    def node_url(self):
        return '<a href="/admin/system/node/%s">%s</a>' % (
                self.node.id, self.node.name)
    node_url.short_description = "Node"
    node_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/node_deployment/one/%s.%s" % (self.id, suffix)
    
class ProductDeployment(crichtonModel):
    product = models.ForeignKey('prodmgmt.Product', related_name="deployments")
    environment = models.ForeignKey('system.Environment', null=True, blank=True,
            related_name="product_deployments")
    insert_date = models.DateTimeField(default = datetime.datetime.now)
    log = CompressedTextField(null=True,blank=True)
    
    class Meta:
        app_label = "deployment"
        ordering = ('insert_date',)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Deleting information about deployments is not allowed.")
    
    def __unicode__(self):
        return "%s -> %s @%s" % (self.product.name,
                self.environment.name or 'unnamed-environment',
                self.insert_date.isoformat())
    
    def product_url(self):
        return '<a href="/admin/prodmgmt/product/%s">%s</a>' % (
                self.product.id, self.product.name)
    product_url.short_description = "Product"
    product_url.allow_tags = True
    
    def environment_url(self):
        return '<a href="/admin/system/environment/%s">%s</a>' % (
                self.environment.id, self.environment.name)
    environment_url.short_description = "Environment"
    environment_url.allow_tags = True

    def get_api_url(self, suffix):
        return "/api/product_deployment/one/%s.%s" % (self.id, suffix)
    
class RecipeManager(models.Manager):
    def get_by_natural_key(self, name, deployment_system_name):
        return self.get(name=name, deployment_system__name=deployment_system_name)

    @commit_or_rollback
    def ensure(self, deployment_system, name):
        result, created = self.get_or_create(name=name,
                deployment_system=deployment_system)
        result.undelete()
        return result, created

class Recipe(crichtonModel):
    objects = RecipeManager()
    name = models.CharField(max_length=255,
            help_text="Identifies this recipe at its deployment system.")
    deployment_system = models.ForeignKey('DeploymentSystem', related_name="recipes")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "deployment"
        unique_together = ("name", "deployment_system")
        ordering = ('name',)

    def __unicode__(self):
        return (self.name or 'unnamed') + '@' + \
                (self.deployment_system and self.deployment_system.name \
                        or 'unnamed-deployment-system')
    
    def natural_key(self):
        return (self.name, self.deployment_system.name)
    natural_key.dependencies = ['deployment.deploymentsystem']
    
    def deployment_system_url(self):
        return '<a href="/admin/deployment/deploymentsystem/%s">%s</a>' % (
                self.deployment_system.id,self.deployment_system.display_name)
    deployment_system_url.short_description = "Deployment system"
    deployment_system_url.allow_tags = True
    
    def package_list_urls(self):
        qs = self.packages.all()
        return ", ".join(['<a href="/admin/package/packagename/%s">%s</a>' % (
                p.package.name, p.package.name) for p in qs])
    package_list_urls.short_description = "Handles packages"
    package_list_urls.allow_tags = True
    
    def get_api_url(self, suffix):
        return "/api/recipe/one/%s@%s.%s" % (self.name, self.deployment_system.name, suffix)

class RecipePackageManager(models.Manager):
    def get_by_natural_key(self, recipe_name, package_name):
        return self.get(recipe__name=name, package__name=package_name)

class RecipePackage(crichtonModel):
    objects = RecipeManager()
    recipe = models.ForeignKey('Recipe', related_name="packages")
    package = models.ForeignKey('package.PackageName', related_name="recipes")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "deployment"
        unique_together = ("recipe", "package")
    
    def __unicode__(self):
        return unicode(self.recipe) + ':' + unicode(self.package)
    
    def natural_key(self):
        return (self.recipe.name, self.package.name)
    natural_key.dependencies = ['deployment.recipe', 'package.packagename']
    
    def get_api_url(self, suffix):
        return "/api/recipe_package/one/%s@%s.%s" % (self.recipe.name, self.package.name, suffix)
    
# eof
