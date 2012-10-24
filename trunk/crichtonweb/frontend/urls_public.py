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
from django.conf.urls.defaults import patterns

def get_s_root():
    from os.path import dirname, abspath, join
    crichtonwebdir=abspath(dirname(__file__))
    sdir=join(crichtonwebdir, "s")
    return sdir

urlpatterns = patterns('',
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/s/img/favicon.ico'}),
    (r'^ping/?$', 'frontend.ping.index', {'format': 'html'}),
    (r'^ping/(?P<format>.*)$', 'frontend.ping.index'),
    #(r'^view/(?P<app_label>[^/]+)/(?P<model_name>[^/]+)/(?P<id>[^/]+)/$', 'frontend.views.view'),
    (r'^s/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': get_s_root(), 'show_indexes': True}),
)


