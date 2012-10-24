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
from django.forms import ModelForm, ModelChoiceField

from ajax_select.fields import AutoCompleteSelectField

from crichtonweb.requirement.models import PackageSpecification, Requirement, VersionRange

class PackageSpecificationForm(ModelForm):
    package = AutoCompleteSelectField('package_name', label='Package Name')

    class Meta:
        model = PackageSpecification

class RequirementForm(ModelForm):
    application = AutoCompleteSelectField('application', label='Requirement')

    class Meta:
        model = Requirement

class VersionRangeForm(ModelForm):
    minimum = AutoCompleteSelectField('version', label='Minimum')
    maximum = AutoCompleteSelectField('version', label='Maximum')

    class Meta:
        model = VersionRange
