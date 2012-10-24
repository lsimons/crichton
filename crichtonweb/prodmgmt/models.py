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

class ApplicationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Application(crichtonModel):
    """
    """
    objects = ApplicationManager()
    name = models.CharField(max_length=128, unique=True,
            help_text="Uniquely identifies the application. Used in URLs.")    
    display_name = models.CharField(max_length=200, blank=True,
            help_text="Human-readable name for the application.")
    product = models.ForeignKey('Product', related_name="applications")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "prodmgmt"
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)
    
    def get_api_url(self, suffix):
        return "/api/application/one/%s.%s" % (self.name, suffix)
    
    def product_url(self):
    # deprecated. use form based on get_absolute_url()
        return self.get_link()
    product_url.short_description = "Product"
    product_url.allow_tags = True

    def is_deployable(self):
        if self.requirement and not self.requirement.deleted:
            return True
        return False
    deployable = property(is_deployable)

class PersonManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(username=username)

class Person(crichtonModel):
    objects = PersonManager()
    # these fields match django.contrib.auth.models.User, which matters
    # make sure to update prodmgmt.utils if you change this
    username = models.CharField(max_length=30, unique=True,
        help_text="Should match jira usernames")
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True,
        help_text="Should be the e-mail address used in the user's SSL certificate")
    distinguished_name = models.CharField(max_length=1024, blank=True,
        help_text="Is the full subject of the user's SSL certificate")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "prodmgmt"
        verbose_name = "person"
        verbose_name_plural = "people"
        ordering = ('username',)

    def __unicode__(self):
        name = ''
        if self.first_name:
            name = self.first_name
            name += ' '
        if self.last_name:
            name += self.last_name
            name += ' '
        if name == '':
            name = self.username
            name += ' '
        #if self.email:
        #    name += '<' + self.email + '>'
        return name.strip()
    
    def natural_key(self):
        return (self.username,)
    
    def get_api_url(self, suffix):
        return "/api/person/one/%s.%s" % (self.username, suffix)

class ProductManager(models.Manager):
    def owned_by_user(self, username):
        rtn = self.get_query_set().filter(owner__username=username)
        return rtn
        
    def followed_by_user(self, username):
        rtn = self.get_query_set().filter(followers__user__username=username)
        return rtn
        
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Product(crichtonModel):
    objects = ProductManager()
    name = models.SlugField(max_length=128, unique=True,
            help_text="Uniquely identifies the product. Used in URLs.")
    display_name = models.CharField(max_length=200, blank=True,
            help_text="The friendly name for the product.")
    owner = models.ForeignKey('Person', related_name="owned_products")
    pipeline_issue = models.ForeignKey('issue.Issue', related_name="+", blank=True, null=True)
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False, help_text="Deleted products are hidden from most views and cannot be released.")
    
    class Meta:
        app_label = "prodmgmt"
        ordering = ('name',)

    def get_api_url(self, suffix):
        return "/api/product/one/%s.%s" % (self.name, suffix)
    
    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)
    
    def application_list_urls(self):
        qs = self.applications.filter(deleted=False)
        return ", ".join(['<a href="/admin/prodmgmt/application/%s">%s</a>' % (
                a.id, a.display_name) for a in qs])
    application_list_urls.short_description = "Applications"
    application_list_urls.allow_tags = True
    
    def build_job_list_urls(self):
        qs = self.build_jobs.filter(deleted=False)
        return ", ".join(['<a href="/admin/ci/buildjob/%s">%s</a>' % (
                b.id, b.name) for b in qs])
    build_job_list_urls.short_description = "Build jobs"
    build_job_list_urls.allow_tags = True
    
    def is_deployable(self):
        has_app = False
        for app in self.applications:
            if app.deleted:
                continue
            has_app = True
            if not app.deployable:
                return False
        return has_app
    deployable = property(is_deployable)

    def ownership_status(self, username):

        if self.owner.username == username:
            return "Owned"
        
        if len(self.followers.filter(user__username=username)):
            return "Following"

        return "Not Following"
            
# why is this crap here? Well, django recommends registering
# your signals in your models.py, to make sure it happens "early
# enough". Experimentally, trying to put it somewhere else is
# not a very good idea.
from django.db.models.signals import post_save
_signals_registered = False
def register_sync_signals():
    global _signals_registered
    if _signals_registered:
        return
    from prodmgmt.utils import sync_person_from_user, sync_user_from_person
    from django.contrib.auth.models import User
    post_save.connect(sync_person_from_user, sender=User)
    post_save.connect(sync_user_from_person, sender=Person)
    _signals_registered = True
register_sync_signals()

# eof
