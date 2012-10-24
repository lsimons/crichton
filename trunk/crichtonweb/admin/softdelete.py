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
def delete_selected(modeladmin, request, queryset):
    queryset.update(deleted=True)
delete_selected.short_description = "Delete selected %(verbose_name_plural)s"

def undelete_selected(modeladmin, request, queryset):
    queryset.update(deleted=False)
undelete_selected.short_description = "Un-delete selected  %(verbose_name_plural)s"
