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
from django.conf.urls.defaults import patterns
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('frontend.views',

    (r'^list_node_names$', 'list_node_names'),
    (r'^get_node_details/(?P<name>.*)$', 'get_node_details'),                       
    (r'^get_node_apps/(?P<name>.*)$', 'get_node_apps'),

    (r'^set_tab_options$', 'set_tab_options'),
    (r'^add_followed_products$', 'add_followed_products'),                       
    (r'^del_followed_products$', 'del_followed_products'),                       

    (r'^list_pipeline_issues$', 'list_pipeline_issues'),
    (r'^list_people$', 'list_people'),
    (r'^list_applications$', 'list_applications'),
                       
    (r'^list_filtered_products$', 'list_filtered_products'),
    (r'^list_packagenames$', 'list_packagenames'),
    (r'^list_versions$', 'list_versions'),
    (r'^get_package_versions/(?P<name>.*)$', 'get_package_versions'),                       

    (r'^load_tab_prodmgmt$', direct_to_template, {'template': 'tab-prodmgmt.html'}),
    (r'^load_tab_release$', direct_to_template, {'template': 'tab-release.html'}),
    (r'^load_tab_build$', direct_to_template, {'template': 'tab-build.html'}),
    (r'^load_orphaned_builds$', direct_to_template, {'template': 'orphaned_builds.html'}),
    (r'^load_tab_node$', direct_to_template, {'template': 'tab-node.html'}),
    (r'^load_tab_package$', 'load_tab_package'),
    (r'^load_tab_options$', 'load_tab_options'),                       
)

urlpatterns += patterns('prodmgmt.views',
    (r'^frm_create_product$', 'frm_product', {'action': 'create', 'id': None}),                      
    (r'^frm_edit_product/(?P<id>.*)$', 'frm_product', {'action': 'edit'}),                       
    (r'^frm_view_product/(?P<id>.*)$', 'frm_product', {'action': 'view'}),                       
    (r'^frm_save_product/(?P<id>.*)$', 'frm_product', {'action': 'save'}),                       
)                        

urlpatterns += patterns('ci.views',
                        (r'^frm_orphan_build_jobs$', 'frm_orphan_build_jobs'),
                        )

#from django.views.generic.simple import direct_to_template
#urlpatterns += patterns('',
#                        (r'^testing', direct_to_template, {'template': 'testing.html'}),
#                        )
