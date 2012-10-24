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
from django.forms import ModelForm

from ajax_select.fields import AutoCompleteSelectField

from crichtonweb.system.models import PoolMembership, NodeAddress, RoleMembership, PackageInstallation

class PoolMembershipForm(ModelForm):
    node = AutoCompleteSelectField('node', label='Node')
    
    class Meta:
        model = PoolMembership

class NodeAddressForm(ModelForm):
    node = AutoCompleteSelectField('node', label='Node')
    address = AutoCompleteSelectField('internet_address', label='Address')

    class Meta:
        model = NodeAddress

class RoleMembershipForm(ModelForm):
    application = AutoCompleteSelectField('application', label='Application')

    class Meta:
        model = RoleMembership

class PackageInstallationForm(ModelForm):
    package = AutoCompleteSelectField('package', label='Package')
    node = AutoCompleteSelectField('node', label='Node')

    class Meta:
        model = PackageInstallation
