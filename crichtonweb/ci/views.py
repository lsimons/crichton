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
from copy import copy

from crichtonweb.ci.models import BuildJob
from crichtonweb.prodmgmt.models import Product
from crichtonweb.ci.forms import OrphanBuildJobsForm
from crichtonweb.frontend.views import json_response, json_response_not_found

def frm_orphan_build_jobs(request):

    if request.method != 'POST':
        return json_response({"status": "err", "error": "Only POSTs expected"})

    # SOCOM-325
    # make a mutable copy of the POST data
    # change it to use the right objects for short-text fields
    #
    # If the amount of text typed is less than the configured minimum for ajax_select,
    # then the data field is empty even though the text field has valid text.
    #
    # (not sure if this is the right place for this.
    # there's probably a django form function where it should go)

    postdata = copy(request.POST)
    if not postdata['build_jobs'] and postdata['build_jobs_text']:
        # minimum number of chars not typed for autocomplete, but it might still be valid
        try:
            bj = BuildJob.objects.get(name=postdata['build_jobs_text'])
            postdata['build_jobs'] = bj.id
        except BuildJob.DoesNotExist:
            pass
    if not postdata['product'] and postdata['product_text']:
        # minimum number of chars not typed for autocomplete, but it might still be valid
        try:
            prod = Product.objects.get(name=postdata['product_text'])
            postdata['product'] = prod.id
        except Product.DoesNotExist:
            pass
        
    # back to normal processing
    form = OrphanBuildJobsForm(postdata)
    if form.is_valid():
        
        build_job = form.cleaned_data['build_jobs']
        build_job.product = form.cleaned_data['product']
        build_job.save()
        
        # If using AutoCompleteSelectMultiple
        ## # update all the buildjobs to link to this product
        ## for build_job in form.cleaned_data['build_jobs']:
        ##     build_job.product = form.cleaned_data['product']
        ##     build_job.save()

        return json_response({"status": "ok"})

    else:
        html = render_to_string('frm_orphan_build_jobs.html', form)
        return json_response({"status": "err", "error": "form not valid", 'html': html})

# eof        
