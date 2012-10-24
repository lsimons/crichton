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
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.shortcuts import render

from release.forms import CloneReleaseForm

@staff_member_required
@csrf_protect
def clone_release(request):
    if request.method == 'POST':
        form = CloneReleaseForm(request.POST)
        if form.is_valid():
            release = form.save(request)
            if form.cleaned_data.has_key('redirecturl'):
                redirecturl = form.cleaned_data['redirecturl']
            else:
                redirecturl = "/"
            return HttpResponseRedirect('/admin/release/release/%d/?redirecturl=%s' % (release.id, redirecturl))
    else:
        form = CloneReleaseForm()
        form.fields['redirecturl'].initial = request.GET.get('redirecturl', None)

    # We add a few extra fields below that are needed for the crumbtrail
    # and would normally be added automatically by the ModelForm if we were 
    # using one.
    data = {
        'form': form,
        'has_change_permission': True,
        'app_label': 'Release',
        'opts': { 'verbose_name_plural': 'Releases'},
        'original': 'Clone release'
    }

    return render(request, 'admin/release/release/clone_form.html', data)

