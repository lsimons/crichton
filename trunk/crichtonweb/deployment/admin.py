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
import crichtonweb.deployment.models as deployment
from crichtonweb.core.register import register
from crichtonweb.admin.admin_audit import AuditedAdmin
from crichtonweb.admin.options import ModelAdmin
import crichtonweb.deployment.admin_inline as deployment_inline
from crichtonweb.deployment.forms import ApplicationDeploymentForm, NodeDeploymentForm, ProductDeploymentForm, RecipePackageForm

class ApplicationDeploymentAdmin(ModelAdmin):
    list_display = ('__unicode__', 'environment_url', 'pool_url', 'insert_date')
    list_display_links = ('__unicode__',)
    date_hierarchy = 'insert_date'
    fields = ('environment', 'pool', 'insert_date', 'recipe', 'product_deployment', 'log')
    raw_id_fields = ('product_deployment',)
    search_fields = ('log', 'environment__name', 'pool__name')
    can_delete = False
    inlines = [deployment_inline.NodeDeploymentInline]
    form = ApplicationDeploymentForm

class DeploymentPreferenceAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'environment_url', 'preference_number', 'deployment_system_url', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted', 'environment', 'deployment_system')
    fields = ('environment', 'preference_number', 'deployment_system', 'deleted')
    search_fields = ('environment__name', 'deployment_system__name')

class DeploymentSystemAdmin(AuditedAdmin):
    list_display = ('name', 'display_name', 'deployment_system_type', 'url_as_url', 'environment_usage_list_urls', 'deleted')
    list_display_links = ('name', 'display_name')
    list_filter = ('deleted',)
    fields = ('display_name', 'name', 'deployment_system_type', 'url',
            'takes_specific_version', 'takes_specific_pool', 'deleted')
    prepopulated_fields = {"name": ("display_name",)}
    search_fields = ('name', 'display_name')
    # takes too long inlines = [deployment_inline.RecipeInline]

class NodeDeploymentAdmin(ModelAdmin):
    list_display = ('__unicode__', 'application_deployment_url', 'node_url', 'succeeded', 'started', 'finished')
    list_display_links = ('__unicode__',)
    date_hierarchy = 'started'
    fields = ('application_deployment', 'node', 'succeeded', 'started', 'finished', 'log')
    raw_id_fields = ('application_deployment',)
    list_filter = ('succeeded',)
    search_fields = ('log', 'node__name', 'application_deployment__log',
            'application_deployment__environment__name',
            'application_deployment__pool__name')
    can_delete = False
    form = NodeDeploymentForm

class ProductDeploymentAdmin(ModelAdmin):
    list_display = ('__unicode__', 'product_url', 'environment_url', 'insert_date')
    list_display_links = ('__unicode__',)
    date_hierarchy = 'insert_date'
    fields = ('product', 'environment', 'insert_date', 'log')
    search_fields = ('log', 'product__name', 'environment__name')
    can_delete = False
    inlines = [deployment_inline.ApplicationDeploymentInline]
    form = ProductDeploymentForm

class RecipeAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'name', 'deployment_system_url', 'package_list_urls', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted', 'deployment_system')
    fields = ('name', 'deployment_system', 'deleted')
    search_fields = ('name', 'deployment_system__name')
    inlines = [deployment_inline.RecipePackageInline]

class RecipePackageAdmin(AuditedAdmin):
    list_display = ('__unicode__', 'deleted')
    list_display_links = ('__unicode__',)
    list_filter = ('deleted',)
    fields = ('recipe', 'package', 'deleted')
    search_fields = ('recipe__name', 'package__name')
    form = RecipePackageForm

# register them all

for model in [deployment.ApplicationDeployment, deployment.DeploymentPreference, deployment.DeploymentSystem, deployment.NodeDeployment, deployment.ProductDeployment, deployment.Recipe, deployment.RecipePackage]:
    register(model, locals())

# eof
