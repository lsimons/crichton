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
from crichtonweb.core.models import crichtonModel

from audit_log.models.managers import AuditLog

from core.utils import commit_or_rollback
from core.introspection_rules import add_rules
add_rules()

class EnvironmentManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
    @commit_or_rollback
    def ensure(self, name):
        environment, created = Environment.objects.get_or_create(name=name)
        environment.undelete()
        return environment, created

class Environment(crichtonModel):
    objects = EnvironmentManager()
    name = models.CharField(max_length=128, unique=True,
            help_text="Uniquely identifies the environment. Used in URLs.")
    repositories = models.ManyToManyField('package.PackageRepository', related_name='environments')
    
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "system"
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)
    
    def get_api_url(self, suffix):
        return "/api/environment/one/%s.%s" % (self.name, suffix)

    def deployment_preference_list_urls(self):
        qs = self.deployment_preferences.filter(deleted=False)
        return ", ".join([dp.get_link() for dp in qs])
    deployment_preference_list_urls.short_description = "Deployment preferences"
    deployment_preference_list_urls.allow_tags = True
    
class InternetAddress(crichtonModel):
    """
    >>> ia = InternetAddress("This text can be anything")
    >>> ia.__unicode__()
    'This text can be anything'
    """
    address = models.CharField(max_length=45, primary_key=True)
    
    class Meta:
        app_label = "system"
        
    def __unicode__(self):
        return self.address

    def get_api_url(self, suffix):
        return "/api/internet_address/one/%s.%s" % (self.address, suffix)
    
class NodeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
    @commit_or_rollback
    def ensure(self, environment, name):
        result, created = self.get_or_create(environment=environment, name=name)
        result.undelete()
        return result, created
    
class Node(crichtonModel):
    objects = NodeManager()
    name = models.CharField(max_length=255, unique=True,
            help_text="The unique host name of this node.")
    is_virtual = models.BooleanField(default=False,
            help_text="Whether this node represents a virtual machine.")
    environment = models.ForeignKey('Environment')
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "system"
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)

    def get_api_url(self, suffix):
        return "/api/node/one/%s.%s" % (self.name, suffix)
    
    def internet_address_list(self):
        qs = self.addresses.all()
        return ", ".join([a.address.address for a in qs])
    internet_address_list.short_description = "IP addresses"
    #internet_address_list.allow_tags = True
    
    def environment_url(self):
        return self.environment.get_link()
    environment_url.short_description = "Environment"
    environment_url.allow_tags = True
    
    def pool_list_urls(self):
        qs = self.pool_memberships.filter(deleted=False)
        return ", ".join([pm.pool.get_link() for pm in qs])
    pool_list_urls.short_description = "Pools"
    pool_list_urls.allow_tags = True


class NodeAddressManager(models.Manager):
    def get_by_natural_key(self, node_name, address):
        return self.get(node__name=node_name, address__address=address)

class NodeAddress(crichtonModel):
    objects = NodeManager()
    node = models.ForeignKey('Node', related_name='addresses')
    address = models.ForeignKey('InternetAddress', related_name='nodes')
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "system"
        unique_together = ("node", "address")
    
    def __unicode__(self):
        return "%s (%s)" % (self.node.name, self.address.address)
    
    def get_api_url(self, suffix):
        return "/api/node_address/one/%s@%s.%s" % (self.node.name, self.address.address, suffix)
    
    def natural_key(self):
        return (self.node.name, self.address.address)
    natural_key.dependencies = ['system.node', 'system.internetaddress']
    
class PoolManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Pool(crichtonModel):
    objects = PoolManager()
    name = models.SlugField(max_length=128, unique=True,
            help_text="The unique host name of this pool. Used in URLs.")
    environment = models.ForeignKey('Environment', related_name="pools")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    role = models.ForeignKey('Role', related_name="pools")
    
    class Meta:
        app_label = "system"
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def get_api_url(self, suffix):
        return "/api/pool/one/%s.%s" % (self.name, suffix)
    
    def natural_key(self):
        return (self.name,)
    
    def _get_short_name(self):
        name = self.name

        role_name = self.role.name
        if name.startswith(role_name):
            name = name[len(role_name):]
            if name.startswith("_"):
                name = name[1:]

        environment_name = self.environment.name
        if name.startswith(environment_name):
            name = name[len(environment_name):]
            if name.startswith("_"):
                name = name[1:]
        if name == "":
            return "pool_1"
        return name
    short_name = property(_get_short_name)
    
    def _get_puppet_name(self):
        return self.role.name + "::" + self.environment.name + "::" + self.short_name
    puppet_name = property(_get_puppet_name)

    def _get_puppet_file_name(self):
        return self.role.name + "_" + self.environment.name + "_" + self.short_name + ".pp"
    puppet_file_name = property(_get_puppet_file_name)
    
    def puppet_application_name(self, application):
        return self.role.puppet_application_name(application, self.environment)
    
    def puppet_application_file_name(self, application):
        return self.role.puppet_application_file_name(application, self.environment)

    def environment_url(self):
        return self.environment.get_link()
    environment_url.short_description = "Environment"
    environment_url.allow_tags = True
    
class PoolMembershipManager(models.Manager):
    def get_by_natural_key(self, node_name, pool_name):
        return self.get(node__name=node_name, pool__name=pool_name)
    
    @commit_or_rollback
    def ensure(self, pool, node):
        result, created = self.get_or_create(pool=pool, node=node)
        result.undelete()
        return result, created

class PoolMembership(crichtonModel):
    objects = PoolMembershipManager()
    node = models.ForeignKey('Node', related_name="pool_memberships")
    pool = models.ForeignKey('Pool', related_name="members")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "system"
        unique_together = ("node", "pool")
        ordering = ('pool', 'node')

    def __unicode__(self):
        return (self.node and self.node.name or 'unnamed-node') + '@' + \
                (self.pool and self.pool.name or 'unnamed-pool')
    
    def get_api_url(self, suffix):
        return "/api/pool_membership/one/%s_%s.%s" % (self.pool.name, self.node.name, suffix)
    
    def natural_key(self):
        return (self.node.name, self.pool.name)
    natural_key.dependencies = ['system.pool', 'system.node']
    
    def node_url(self):
        return self.node.get_link()
    node_url.short_description = "Node"
    node_url.allow_tags = True
    
    def pool_url(self):
        return self.pool.get_link()
    pool_url.short_description = "Pool"
    pool_url.allow_tags = True

class RoleManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Role(crichtonModel):
    # like http://wiki.opscode.com/display/chef/Roles
    objects = PoolManager()
    name = models.SlugField(max_length=128, unique=True,
            help_text="The unique name of this role. Used in URLs.")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "system"
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def get_api_url(self, suffix):
        return "/api/role/one/%s.%s" % (self.name, suffix)
    
    def natural_key(self):
        return (self.name,)
    
    def _get_puppet_name(self):
        return self.name
    puppet_name = property(_get_puppet_name)

    def _get_puppet_file_name(self):
        return self.name + ".pp"
    puppet_file_name = property(_get_puppet_file_name)
    
    def puppet_application_name(self, application, environment):
        return self.name + "::" + environment.name + "::" + application.name
    
    def puppet_application_file_name(self, application, environment):
        return self.name + "_" + environment.name + "_" + application.name + ".pp"
    
    def puppet_environment_name(self, environment):
        return self.name + "::" + environment.name
    
    def puppet_environment_file_name(self, environment):
        return self.name + "_" + environment.name + ".pp"

class RoleMembershipManager(models.Manager):
    def get_by_natural_key(self, role_name, application_name):
        return self.get(role__name=role_name, application__name=application_name)

class RoleMembership(crichtonModel):
    objects = RoleMembershipManager()
    role = models.ForeignKey('Role', related_name="applications")
    application = models.ForeignKey('prodmgmt.Application', related_name="roles")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "system"
        unique_together = ("role", "application")

    def __unicode__(self):
        return self.role.name + ':' + self.application.name
    
    def get_api_url(self, suffix):
        return "/api/role_membership/one/%s:%s.%s" % (self.role.name, self.application.name, suffix)
    
    def natural_key(self):
        return (self.role.name, self.application.name)
    natural_key.dependencies = ['system.role', 'prodmgmt.application']

class  crichtonStatusType(crichtonModel):
    """
        This is a parent for possible different crichton status types.
        Every new status type should inherit from this parent.

        There are not going to be any records for this parent in database.
    """
    name = models.CharField(max_length=128, help_text="The unique name of status. Used in URLs.", unique=True, null=False, blank=False)
    # Django model inheritance does not support field overwriting :( , so I will rather comment this out
    #status = models.CharField(max_length=100, help_text="Status", null=False, blank=False)
    comment = models.CharField(max_length=1024, help_text="Comment", null=True, blank=True)
    date = models.DateTimeField('Created / Updated', null=False, blank=False)
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class crichtonStatusTypeManager(models.Manager):
    """
        This is a parent for possible different crichton status type managers.
        Every new status manager type should inherit from this parent.
    """
    def get_by_natural_key(self, name):
        return self.get(name = name)

    @commit_or_rollback
    def ensure(self, name, status, comment=None, date=None):
        if not date:
            date = datetime.datetime.now()
        cronJob, created = self.get_or_create(name=name, status=status, comment=comment, date=date)
        cronJob.undelete()
        return cronJob, created

    class Meta:
        abstract = True

class crichtonCronJobStatusManager(crichtonStatusTypeManager):
    """
       The crichton cron job manager defines some handy methods.
    """
    @commit_or_rollback
    def update_success(self, name):
        self.filter(name=name).update(status='Successful', date=datetime.datetime.now())

    @commit_or_rollback
    def update_failure(self, name):
        self.filter(name=name).update(status='Failed', date=datetime.datetime.now())

class crichtonCronJobStatus(crichtonStatusType):
    """
        To represent the crichtons' cron jobs statuses
    """
    STATUS_CHOICES = (
        ( 'S', 'Successful' ),
        ( 'F', 'Failed' ),
    )
    objects = crichtonCronJobStatusManager()
    # overwrite general definition
    status = models.CharField(max_length=100, help_text="Status", choices=STATUS_CHOICES, null=False, blank=False)

    class Meta:
        app_label = "system"
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def get_api_url(self, suffix):
        return "/api/crichton_cron_job_status/one/%s.%s" % (self.name, suffix)

class PackageInstallationManager(models.Manager):
    @commit_or_rollback
    def ensure(self, package, node, seen_at=None):
        try:
            package_installation = self.get(package=package, node=node, not_seen=None)
            created = False
        except PackageInstallation.DoesNotExist:
            if not seen_at:
                seen_at = datetime.datetime.now()
            package_installation =  self.create(package=package, node=node, first_seen=seen_at)
            created = True
        return package_installation, created
    
    @commit_or_rollback
    def update_not_seen(self, node, packages_seen, not_seen_at=None):
        if not not_seen_at:
            not_seen_at = datetime.datetime.now()
        return self.filter(node=node, not_seen=None).exclude(package__in=packages_seen).update(not_seen=not_seen_at)

class PackageInstallation(crichtonModel):
    objects = PackageInstallationManager()
    package = models.ForeignKey('package.Package', related_name="installations", db_index=True)
    node = models.ForeignKey('system.Node', related_name="package_installations", db_index=True)
    first_seen = models.DateTimeField(db_index=True)
    not_seen = models.DateTimeField(null=True, blank=True, db_index=True)
    can_delete = False

    class Meta:
        app_label = "system"
        unique_together = ('node', 'package', 'not_seen')
        # django doesn't support multi-column indexes
        # http://code.djangoproject.com/ticket/5805
        # index_together = (('package', 'not_seen'), ('node', 'not_seen'))
    
    def __unicode__(self):
        return "%s:%s:%s->%s" % (unicode(self.package), unicode(self.node), unicode(self.first_seen), unicode(self.not_seen))

    def get_api_url(self, suffix):
        return "/api/package_installation/one/%s" % (self.id,)

# # eof
