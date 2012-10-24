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
from django.contrib import admin as origadmin

from crichtonweb.admin import mysite
import crichtonweb.prodmgmt.models as prodmgmt
from crichtonweb.prodmgmt.forms import ProductForm
from crichtonweb.core.register import register
from crichtonweb.admin.admin_audit import AuditedAdmin
import crichtonweb.system.admin_inline as system_inline
import crichtonweb.prodmgmt.admin_inline as prodmgmt_inline
import crichtonweb.release.admin_inline as release_inline
from crichtonweb.prodmgmt.forms import ApplicationForm

class ApplicationAdmin(AuditedAdmin):
    list_display = ('name', 'display_name', 'product_url', 'deleted')
    list_display_links = ('name', 'display_name')
    list_filter = ('deleted',)
    fields = ('display_name', 'name', 'product', 'deleted')
    prepopulated_fields = {"name": ("display_name",)}
    search_fields = ('name', 'display_name', 'product__name', 'product__display_name')
    inlines = [system_inline.RoleMembershipInline]
    form = ApplicationForm

class PersonAdmin(AuditedAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'deleted')
    list_display_links = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('deleted',)
    fields = ('username', 'first_name', 'last_name', 'email', 'deleted')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    inlines = [prodmgmt_inline.ProductInline]

class ProductAdmin(AuditedAdmin):
    list_display = ('name', 'display_name', 'owner', 'application_list_urls', 'build_job_list_urls', 'deleted',)
    list_display_links = ('name', 'display_name')
    list_filter = ('deleted',)
    fields = ('display_name', 'name', 'owner', 'pipeline_issue', 'deleted')
    prepopulated_fields = {"name": ("display_name",)}
    search_fields = ('name', 'display_name', 'owner__name')
    # inline adding of build jobs does not actually make much sense since we want users to link existing, instead
    # inlines = [prodmgmt_inline.ApplicationInline, release_inline.ReleaseInline, ci_inline.BuildJobInline]
    inlines = [prodmgmt_inline.ApplicationInline, release_inline.ReleaseInline]
    
    form = ProductForm

# register them all

for model in [prodmgmt.Application, prodmgmt.Person, prodmgmt.Product]:
    register(model, locals())

# eof
