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
from django.forms import ModelForm, Form, CharField, ModelMultipleChoiceField

from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField


from crichtonweb.ci.models import BuildJob, BuildResult

class BuildJobForm(ModelForm):
    product = AutoCompleteSelectField('product', required=False, label='Product')

    class Meta:
        model = BuildJob

class BuildResultForm(ModelForm):
    job = AutoCompleteSelectField('build_job', label='Build Job')
    produced_package = AutoCompleteSelectField('package', label='Produced package')
    
    class Meta:
        model = BuildResult

class OrphanBuildJobsForm(Form):
    """ Allows user to select and link build jobs to one product """
    
    product = AutoCompleteSelectField('product', required=True, label='Product')
    # MultipleField is throwing an error at the moment,
    # so just allow one at once for the moment
    # FIXME
    #build_jobs = AutoCompleteSelectMultipleField('orphan_build_job', required=True)
    build_jobs = AutoCompleteSelectField('orphan_build_job', required=True, label='Build Job')

    #
    # This is needed for AutoCompleteSelectMultipleField
    ## def clean(self):
    ##     # AutoCompleteSelectField returns the object,
    ##     # but AutoCompleteSelectMultipleFields returns a list of ids,
    ##     # so we'll have to do the cleaning

    ##     from pdb import set_trace
    ##     set_trace()
    ##     build_jobs = []
    ##     for x in self.cleaned_data['build_jobs']:
    ##         try:
    ##             build_jobs.append(BuildJob.objects.get(id=x))
    ##         except BuildJob.DoesNotExist:
    ##             raise ValidationError("Cannot find BuildJob for id '%s'" % x)
    ##     self.cleaned_data['build_jobs'] = build_jobs
    ##     return self.cleaned_data
    
# eof
