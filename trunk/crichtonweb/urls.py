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
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic import TemplateView

# http://code.djangoproject.com/ticket/10405#comment:11
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache.get_models()

from crichtonweb.admin import mysite

import crichtonweb.ci.admin
import crichtonweb.core.admin
import crichtonweb.deployment.admin
import crichtonweb.frontend.admin
import crichtonweb.issue.admin
import crichtonweb.jirarpc.admin
import crichtonweb.package.admin
import crichtonweb.prodmgmt.admin
import crichtonweb.release.admin
import crichtonweb.requirement.admin
import crichtonweb.system.admin

from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from crichtonweb.admin import mysite
mysite.register(Group, GroupAdmin)
mysite.register(User, UserAdmin)

urlpatterns = patterns('', 
    (r'^$', direct_to_template,
            {'template': 'crichton_user.html', 'extra_context':{'title': 'Home'}}),
                       
    (r'^ajax_select/', include('ajax_select.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/release/deploymentrequest/jira_error', TemplateView.as_view(template_name="jira_error.html")),
    (r'^admin/release/release/clone/', 'release.admin_views.clone_release'),
    (r'^admin/', include(mysite.urls)),
    
    #(r'^search/', include('haystack.urls')),
    
    (r'^api/', include('api.services')),
    (r'^jirarpc/', include('jirarpc.urls')),
    (r'', include('frontend.urls_public')),
    (r'^admin/frontend/', include('frontend.urls_private')),
    (r'', include(mysite.urls)),
)

# eof
