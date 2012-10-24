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
import crichtonweb.release.models as release
from crichtonweb.release.forms import ReleaseForm, ReleaseElementForm

class ReleaseInline(origadmin.TabularInline):
    model = release.Release
    extra = 0
    fields = ('product', 'version', 'release_order', 'deleted')
    form = ReleaseForm

class ReleaseElementInline(origadmin.TabularInline):
    model = release.ReleaseElement
    extra = 0
    fields = ('release', 'package', 'application', 'deleted')
    form = ReleaseElementForm
    
    def get_formset(self, request, obj, *args, **kwargs):
        if obj and obj.deployment_requests.exists():
            kwargs["max_num"] = 0
        return super(ReleaseElementInline, self).get_formset(request, obj, *args, **kwargs)
