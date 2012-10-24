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
from crichtonweb.core.lookups import BaseLookup, NamedLookup
from crichtonweb.system.models import Node, InternetAddress
from django.db.models import Q

class NodeLookup(NamedLookup):
    model = Node

class InternetAddressLookup(BaseLookup):
    model = InternetAddress

    def get_filter(self, term):
        return self.model.objects.filter(
            Q(address__istartswith=term)
        )
    
    def order(self, qs):
        return qs.order_by('address')
